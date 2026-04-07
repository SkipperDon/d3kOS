<?php
/**
 * admin-api-tickets.php — AtMyBoat.com Admin CRM: Support Tickets API
 * v0.9.7 Phase 1: Ticket list, ticket detail, ticket update (status + admin_note).
 *
 * Auth:   X-Admin-Key header (AMBOAT_ADMIN_API_KEY from config.php)
 * Method: POST, JSON body: { "action": "...", ... }
 *
 * Actions:
 *   get_tickets    — paginated list, optional status filter
 *   get_ticket     — single ticket detail
 *   update_ticket  — set status + admin_note
 */

require_once __DIR__ . '/config.php';

// Same key as admin-api.php
if (!defined('ADMIN_API_KEY')) {
    define('ADMIN_API_KEY', 'amboat_admin_74899205409692603cb9c951c3c895ce27d92599');
}

header('Content-Type: application/json');

// ── Auth — Bearer token (same pattern as admin-api.php) ──────────────────────
$auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
if ($auth_header !== 'Bearer ' . ADMIN_API_KEY) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

// ── Parse body ────────────────────────────────────────────────────────────────
$body   = json_decode(file_get_contents('php://input'), true) ?? [];
$action = $body['action'] ?? '';

try {
    $pdo = new PDO(
        'mysql:host=127.0.0.1;dbname=atmyb197_wp302;charset=utf8mb4',
        'atmyb197_wp302', 'atmyboat2026',
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'DB error']);
    exit;
}

switch ($action) {

    // ── get_tickets ───────────────────────────────────────────────────────────
    // Body: { action, status?, page? }
    // Returns: { tickets: [...], total, page, pages }
    case 'get_tickets': {
        $page    = max(1, (int)($body['page'] ?? 1));
        $limit   = 25;
        $offset  = ($page - 1) * $limit;
        $status  = $body['status'] ?? '';

        $where  = '';
        $params = [];
        if (in_array($status, ['open', 'in_progress', 'resolved'], true)) {
            $where    = 'WHERE t.status = ?';
            $params[] = $status;
        }

        $count_sql = "SELECT COUNT(*) FROM amboat_support_tickets t $where";
        $stmt = $pdo->prepare($count_sql);
        $stmt->execute($params);
        $total = (int)$stmt->fetchColumn();

        $sql = "SELECT t.ticket_id, t.user_id, t.subject, t.status,
                       t.created_at, t.updated_at,
                       u.display_name, u.user_email
                FROM amboat_support_tickets t
                LEFT JOIN wpax_users u ON u.ID = t.user_id
                $where
                ORDER BY t.created_at DESC
                LIMIT $limit OFFSET $offset";
        $stmt = $pdo->prepare($sql);
        $stmt->execute($params);
        $tickets = $stmt->fetchAll(PDO::FETCH_ASSOC);

        echo json_encode([
            'success' => true,
            'tickets' => $tickets,
            'total'   => $total,
            'page'    => $page,
            'pages'   => (int)ceil($total / $limit),
        ]);
        break;
    }

    // ── get_ticket ────────────────────────────────────────────────────────────
    // Body: { action, ticket_id }
    // Returns: full ticket detail including admin_note
    case 'get_ticket': {
        $ticket_id = (int)($body['ticket_id'] ?? 0);
        if ($ticket_id < 1) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'ticket_id required']);
            exit;
        }

        $stmt = $pdo->prepare(
            "SELECT t.ticket_id, t.user_id, t.device_token, t.subject, t.body,
                    t.status, t.admin_note, t.created_at, t.updated_at,
                    u.display_name, u.user_email,
                    um.meta_value AS tier
             FROM amboat_support_tickets t
             LEFT JOIN wpax_users u ON u.ID = t.user_id
             LEFT JOIN wpax_usermeta um ON um.user_id = t.user_id AND um.meta_key = 'atmyboat_tier'
             WHERE t.ticket_id = ?
             LIMIT 1"
        );
        $stmt->execute([$ticket_id]);
        $ticket = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$ticket) {
            http_response_code(404);
            echo json_encode(['success' => false, 'error' => 'Ticket not found']);
            exit;
        }

        echo json_encode(['success' => true, 'ticket' => $ticket]);
        break;
    }

    // ── update_ticket ─────────────────────────────────────────────────────────
    // Body: { action, ticket_id, status?, admin_note? }
    // Returns: { success, updated_at }
    case 'update_ticket': {
        $ticket_id  = (int)($body['ticket_id'] ?? 0);
        $new_status = $body['status'] ?? '';
        $admin_note = $body['admin_note'] ?? null;

        if ($ticket_id < 1) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'ticket_id required']);
            exit;
        }

        $valid_statuses = ['open', 'in_progress', 'resolved'];
        if ($new_status && !in_array($new_status, $valid_statuses, true)) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Invalid status']);
            exit;
        }

        // Build SET clause dynamically — only update supplied fields
        $sets   = ['updated_at = NOW()'];
        $params = [];

        if ($new_status) {
            $sets[]   = 'status = ?';
            $params[] = $new_status;
        }
        if ($admin_note !== null) {
            $sets[]   = 'admin_note = ?';
            $params[] = $admin_note ?: null;
        }

        $params[] = $ticket_id;

        $stmt = $pdo->prepare(
            'UPDATE amboat_support_tickets SET ' . implode(', ', $sets) . ' WHERE ticket_id = ?'
        );
        $stmt->execute($params);

        if ($stmt->rowCount() === 0) {
            http_response_code(404);
            echo json_encode(['success' => false, 'error' => 'Ticket not found']);
            exit;
        }

        $stmt2 = $pdo->prepare('SELECT updated_at FROM amboat_support_tickets WHERE ticket_id = ?');
        $stmt2->execute([$ticket_id]);
        $updated_at = $stmt2->fetchColumn();

        echo json_encode(['success' => true, 'updated_at' => $updated_at]);
        break;
    }

    default:
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Unknown action']);
}
