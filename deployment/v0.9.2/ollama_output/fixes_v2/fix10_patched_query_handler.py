def query(self, question, force_provider=None, quick_mode=None):
        """
        Simplified query handler - RAG-only manual search
        
        Args:
            question: The user's question
            force_provider: Ignored (kept for API compatibility)
            quick_mode: Ignored (always uses RAG-only)
        
        Returns:
            dict with answer, provider, model, response_time, manual_used
        """
        start_time = time.time()
        manual_context = None
        manual_used = False
        
        # Check for action commands FIRST (log note, set alarm, etc.)
        action = self.classify_action_query(question)
        if action:
            action_type, payload = action
            print(f"  ⚡ Action command: {action_type}", flush=True)
            answer = self.execute_action(action_type, payload)
            elapsed = time.time() - start_time
            response_time = int(elapsed * 1000)
            self.store_conversation(question, answer, 'onboard', 'action', 'rules', response_time)
            return {
                'question': question,
                'answer': answer,
                'provider': 'action',
                'model': 'rules',
                'ai_used': 'onboard',
                'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat(),
                'manual_used': False
            }

        # Check if simple query (rule-based patterns)
        simple_category = self.classify_simple_query(question)
        if simple_category:
            # Use rule-based response immediately (RPM, oil, temp, etc.)
            answer = self.simple_response(simple_category)
            elapsed = time.time() - start_time
            response_time = int(elapsed * 1000)
            
            # Store in database
            self.store_conversation(question, answer, 'onboard', 'onboard', 'rules', response_time)
            
            return {
                'question': question,
                'answer': answer,
                'provider': 'onboard',
                'model': 'rules',
                'ai_used': 'onboard',
                'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat(),
                'manual_used': False
            }
        
        # Complex query - search manuals for context
        print("  🔍 Searching manuals for relevant information...", flush=True)
        rag_results = self.search_manuals(question, k=6)  # Increased from 4 to 6
        
        # Filter weak results by distance
        MAX_DISTANCE = 0.40
        results = [r for r in rag_results if r.get('distance', 1.0) < MAX_DISTANCE]
        if not results:
            # No strong matches — fall through to Gemini
            return self._query_gemini(query)
        
        # Build RAG context with source info
        context_parts = []
        for r in results:
            source = r.get('metadata', {}).get('source', 'unknown')
            context_parts.append(f"[Source: {source}]\n{r['document']}")
        rag_context = '\n\n'.join(context_parts)
        
        manual_context = rag_context
        manual_used = bool(manual_context)

        if manual_context:
            print("  ✓ Found relevant manual information", flush=True)
        else:
            print("  ℹ️  No relevant manual information found", flush=True)

        # Try Gemini first (faster, smarter responses)
        boat_status = self.get_boat_status()
        print("  🤖 Querying Gemini...", flush=True)
        gemini_answer = self._query_gemini(question, boat_status)

        if gemini_answer:
            answer = gemini_answer
            provider = 'gemini'
            model = 'gemini-api'
            print("  ✓ Gemini responded", flush=True)
        else:
            # Fallback: show RAG results directly
            answer = self.format_quick_answer(question, manual_context)
            provider = 'rag-only'
            model = 'manual-search'
            print("  ℹ️  Gemini unavailable, using RAG results", flush=True)

        elapsed = time.time() - start_time
        response_time = int(elapsed * 1000)

        ai_used = 'online' if provider == 'gemini' else 'onboard'
        self.store_conversation(question, answer, ai_used, provider, model, response_time)

        return {
            'question': question,
            'answer': answer,
            'provider': provider,
            'model': model,
            'ai_used': provider,
            'response_time_ms': response_time,
            'timestamp': datetime.now().isoformat(),
            'manual_used': manual_used
        }