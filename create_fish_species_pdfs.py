#!/usr/bin/env python3
"""
Create Fish Species PDFs for RAG Integration
Converts Great Lakes fish species data into individual PDF files
"""
import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Fish species data
FISH_SPECIES = [
    # Priority 1: Game Fish
    {
        "common_name": "Yellow Perch",
        "scientific_name": "Perca flavescens",
        "family": "Percidae (Perch Family)",
        "native": True,
        "description": "Yellow Perch is the dominant species in Lake Simcoe, representing 94% of winter catch and 66% of summer catch. This native fish is highly prized for both its fighting ability and excellent table fare.",
        "visual_characteristics": "Body is yellow to brassy green with 6-9 dark vertical bars along the sides. Fins are orange to red, particularly the pelvic and anal fins. Adult fish have a distinctly humped back.",
        "habitat": "Prefers shallow weedy areas in spring and summer, moving to deeper water in fall and winter. Found throughout Lake Simcoe and all Great Lakes. Thrives in cool water temperatures.",
        "size_range": "Typical: 15-30 cm (6-12 inches). Lake Simcoe is famous for 14+ inch 'jumbo perch'.",
        "distribution": "Native to Great Lakes, Lake Simcoe, and throughout Ontario waters. One of the most abundant species.",
        "regulations": "Check Ontario fishing regulations for current size and bag limits. Lake Simcoe has specific perch regulations."
    },
    {
        "common_name": "Largemouth Bass",
        "scientific_name": "Micropterus salmoides",
        "family": "Centrarchidae (Sunfish Family)",
        "native": True,
        "description": "Largemouth Bass is a popular gamefish found in shallow weedy areas of Lake Simcoe and throughout the Great Lakes. Known for aggressive strikes and powerful runs.",
        "visual_characteristics": "Dark green to olive coloring with a dark lateral band running from head to tail. Large mouth extends past the eye. Upper jaw reaches beyond rear edge of eye (distinguishes from Smallmouth Bass).",
        "habitat": "Shallow weedy areas, submerged structures, lily pads, and vegetated shorelines. Prefers warmer water than Smallmouth Bass.",
        "size_range": "Typical: 30-50 cm (12-20 inches). Trophy fish can exceed 55 cm (22 inches).",
        "distribution": "Lake Simcoe, all Great Lakes, rivers, and inland lakes throughout Ontario.",
        "regulations": "Check Ontario fishing regulations. Closed season typically late spring to early summer to protect spawning fish."
    },
    {
        "common_name": "Smallmouth Bass",
        "scientific_name": "Micropterus dolomieu",
        "family": "Centrarchidae (Sunfish Family)",
        "native": True,
        "description": "Smallmouth Bass averages 5+ pounds in Lake Simcoe and is prized for its acrobatic fighting ability. Considered by many anglers to be the best pound-for-pound fighter in freshwater.",
        "visual_characteristics": "Bronze to brown coloring with dark vertical bars or blotches. Red eye is distinctive. Mouth is smaller than Largemouth Bass, with upper jaw not extending past the rear of the eye.",
        "habitat": "Rocky areas, drop-offs, shoals, and points. Prefers cooler, clearer water than Largemouth Bass. Found at depths of 5-30 feet.",
        "size_range": "Lake Simcoe average: 5+ pounds. Typical: 30-45 cm (12-18 inches).",
        "distribution": "Abundant in Lake Simcoe, all Great Lakes, and rocky lakes throughout Ontario.",
        "regulations": "Check Ontario fishing regulations. Closed season typically late spring to early summer."
    },
    {
        "common_name": "Northern Pike",
        "scientific_name": "Esox lucius",
        "family": "Esocidae (Pike Family)",
        "native": True,
        "description": "Native aggressive predator found throughout Lake Simcoe. Known for explosive strikes and can grow to 40+ inches. Pike are ambush predators that strike from cover.",
        "visual_characteristics": "Long torpedo-shaped body with dark green back fading to lighter green or yellow sides. Body covered with light yellow-white bean-shaped spots. Duck-bill shaped snout with sharp teeth.",
        "habitat": "Shallow weedy bays in spring, deeper weed edges and drop-offs in summer. Ambush predators that hide in vegetation.",
        "size_range": "Lake Simcoe: commonly 40+ inches. Typical: 50-100 cm (20-40 inches). Trophy fish can exceed 120 cm (48 inches).",
        "distribution": "Throughout Lake Simcoe, all Great Lakes, and most Ontario waters. One of the most widespread native species.",
        "regulations": "Check Ontario fishing regulations for size limits and seasons. Some waters have slot limits to protect breeding stock."
    },
    {
        "common_name": "Lake Trout",
        "scientific_name": "Salvelinus namaycush",
        "family": "Salmonidae (Salmon Family)",
        "native": True,
        "description": "Native char species that can grow to 20+ pounds in Lake Simcoe. Prefers deep, cold water and is highly prized by anglers. Lake Simcoe is renowned for its trophy lake trout fishery.",
        "visual_characteristics": "Dark grey to greenish body with light irregular spots and vermiculations (worm-like markings). Deeply forked tail. No black spots on dorsal or adipose fin (distinguishes from Brook Trout).",
        "habitat": "Deep cold water, typically 50-100 feet in summer. Found in shallower water (15-30 feet) in spring and fall when water temperatures drop. Requires cold, well-oxygenated water year-round.",
        "size_range": "Lake Simcoe: 20+ pounds common. Typical: 50-75 cm (20-30 inches). Trophy fish can exceed 90 cm (36 inches) and 25 pounds.",
        "distribution": "Native to Lake Simcoe, Lake Superior, Lake Huron, deep lakes in Northern Ontario. Requires cold-water habitat.",
        "regulations": "Check Ontario fishing regulations. Lake Simcoe has specific Lake Trout regulations including slot limits."
    },
    {
        "common_name": "Walleye",
        "scientific_name": "Sander vitreus",
        "family": "Percidae (Perch Family)",
        "native": True,
        "description": "Native top predator and culinary favorite throughout the Great Lakes. Lake Erie is world-renowned for trophy walleye fishing. Excellent table fare with firm white flesh.",
        "visual_characteristics": "Olive-brown back fading to golden yellow sides. White tip on lower lobe of tail fin. Large glassy eyes adapted for low-light vision. Dark blotch at rear of first dorsal fin.",
        "habitat": "Rocky reefs, drop-offs, weed edges, and river mouths. Most active at dawn, dusk, and night. Moves to deeper water during bright sunlight.",
        "size_range": "Typical: 35-60 cm (14-24 inches). Lake Erie trophy fish can exceed 75 cm (30 inches) and 10 pounds.",
        "distribution": "Lake Erie (trophy fishery), Lake Huron, inland lakes throughout Ontario. Stocked in some waters.",
        "regulations": "Check Ontario fishing regulations. Size and bag limits vary by water body. Lake Erie has specific walleye regulations."
    },
    {
        "common_name": "Muskellunge",
        "scientific_name": "Esox masquinongy",
        "family": "Esocidae (Pike Family)",
        "native": True,
        "description": "Native trophy fish found in the Great Lakes. Known as the 'fish of 10,000 casts' due to its elusive nature. Largest member of the pike family in North America.",
        "visual_characteristics": "Similar to Northern Pike but with dark bars or spots on light background (opposite of pike). Pointed lobes on tail fin. Usually 6-9 sensory pores on underside of lower jaw (pike has 5 or fewer).",
        "habitat": "Large weedy bays, rocky shoals, and weed edges of large lakes. Adults prefer deeper water than Northern Pike.",
        "size_range": "Trophy fish: 100-140 cm (40-55 inches), 20-40 pounds. Can exceed 150 cm (60 inches) and 50 pounds.",
        "distribution": "Lake Huron, Lake St. Clair, Georgian Bay, and select inland lakes. Requires large water bodies.",
        "regulations": "Check Ontario fishing regulations. Many waters have minimum size limits (36-54 inches) to protect breeding stock. Catch-and-release encouraged."
    },
    {
        "common_name": "Lake Whitefish",
        "scientific_name": "Coregonus clupeaformis",
        "family": "Salmonidae (Salmon Family)",
        "native": True,
        "description": "Native species, stocked annually in Lake Simcoe (140,000+ fish). Excellent table fare with delicate white flesh. Important commercial and recreational species.",
        "visual_characteristics": "Silver body with olive to dark grey back. Small head with blunt snout that overhangs mouth. Deeply forked tail. Adipose fin present.",
        "habitat": "Deep cold water, typically 30-100 feet. Feeds on bottom-dwelling organisms. Moves to shallow reefs for spawning in late fall.",
        "size_range": "Typical: 30-50 cm (12-20 inches), 1-4 pounds. Can reach 60 cm (24 inches) and 7 pounds.",
        "distribution": "Native to Lake Simcoe (stocked annually), all Great Lakes, and deep cold-water lakes in Northern Ontario.",
        "regulations": "Check Ontario fishing regulations. Open season varies by water body."
    },
    {
        "common_name": "Bluegill",
        "scientific_name": "Lepomis macrochirus",
        "family": "Centrarchidae (Sunfish Family)",
        "native": True,
        "description": "Native to Great Lakes region, expanding population in Lake Simcoe. Excellent panfish for family fishing. Provides year-round fishing opportunities.",
        "visual_characteristics": "Deep-bodied and laterally compressed. Dark blue to purple coloring on cheek and gill cover. Dark blotch on rear of dorsal fin. Breeding males have orange-red breast.",
        "habitat": "Shallow weedy areas, around docks and submerged vegetation. Forms large schools. Prefers warm water.",
        "size_range": "Typical: 10-20 cm (4-8 inches). Trophy fish can reach 25 cm (10 inches).",
        "distribution": "Lake Simcoe (expanding), all Great Lakes, ponds and lakes throughout Southern Ontario.",
        "regulations": "Check Ontario fishing regulations. Generally liberal limits to encourage harvest."
    },
    {
        "common_name": "Black Crappie",
        "scientific_name": "Pomoxis nigromaculatus",
        "family": "Centrarchidae (Sunfish Family)",
        "native": True,
        "description": "Native species with stable population in Lake Simcoe. Excellent eating, forms large schools making them a popular target for ice anglers.",
        "visual_characteristics": "Silver-olive body with irregular black blotches and speckles. Deep-bodied and laterally compressed. 7-8 dorsal fin spines (White Crappie has 5-6).",
        "habitat": "Prefers clear water with moderate vegetation. Found near submerged brush, fallen trees, and dock pilings. Forms large schools.",
        "size_range": "Typical: 20-30 cm (8-12 inches), 0.5-1 pound. Trophy fish can exceed 35 cm (14 inches) and 2 pounds.",
        "distribution": "Lake Simcoe (stable population), all Great Lakes, lakes and reservoirs throughout Ontario.",
        "regulations": "Check Ontario fishing regulations. Generally liberal limits."
    },
    {
        "common_name": "Burbot",
        "scientific_name": "Lota lota",
        "family": "Gadidae (Cod Family)",
        "native": True,
        "description": "Only freshwater member of the cod family in North America. Important winter fishery in Lake Simcoe. Most active in cold water and at night.",
        "visual_characteristics": "Eel-like body with mottled brown-olive coloring. Single barbel on chin. Two dorsal fins (first short, second very long). Rounded tail.",
        "habitat": "Deep cold water over rocky or muddy bottom. Most active in winter, spawning under ice. Moves to deeper water in summer.",
        "size_range": "Typical: 30-60 cm (12-24 inches), 1-4 pounds. Can exceed 75 cm (30 inches) and 8 pounds.",
        "distribution": "Lake Simcoe (winter fishery), Lake Superior, Lake Huron, deep cold lakes in Northern Ontario.",
        "regulations": "Check Ontario fishing regulations. Open season typically winter months."
    },
    {
        "common_name": "Chinook Salmon",
        "scientific_name": "Oncorhynchus tshawytscha",
        "family": "Salmonidae (Salmon Family)",
        "native": False,
        "description": "Introduced Pacific salmon, most popular salmon species in Great Lakes. Trophy fish can exceed 20 pounds. Die after spawning (semelparous).",
        "visual_characteristics": "Silver sides when in lake, turning dark with red-brown coloring during spawning. Black spots on back, dorsal fin, and both lobes of tail. Black gums (distinguishes from Coho).",
        "habitat": "Open water of Great Lakes, chasing baitfish. Enter tributaries in fall to spawn. Prefer water temperature 50-60°F.",
        "size_range": "Typical: 60-90 cm (24-36 inches), 10-25 pounds. Trophy fish can exceed 100 cm (40 inches) and 35 pounds.",
        "distribution": "All Great Lakes, tributaries for spawning. Most common in Lake Ontario, Lake Michigan, Lake Huron.",
        "regulations": "Check Ontario fishing regulations. Open season typically spring through fall."
    },
    {
        "common_name": "Coho Salmon",
        "scientific_name": "Oncorhynchus kisutch",
        "family": "Salmonidae (Salmon Family)",
        "native": False,
        "description": "Introduced Pacific salmon, popular gamefish in Great Lakes. Excellent fighter with spectacular aerial displays. Die after spawning.",
        "visual_characteristics": "Silver sides with small black spots on back and upper lobe of tail only (not lower lobe). White gums (distinguishes from Chinook). Turns dark red during spawning.",
        "habitat": "Open water of Great Lakes. Enter tributaries in fall to spawn. More aggressive feeder than Chinook.",
        "size_range": "Typical: 45-65 cm (18-26 inches), 5-10 pounds. Can exceed 75 cm (30 inches) and 15 pounds.",
        "distribution": "All Great Lakes, tributaries for spawning. Common in Lake Ontario, Lake Michigan, Lake Huron.",
        "regulations": "Check Ontario fishing regulations. Open season typically spring through fall."
    },
    {
        "common_name": "Rainbow Trout / Steelhead",
        "scientific_name": "Oncorhynchus mykiss",
        "family": "Salmonidae (Salmon Family)",
        "native": False,
        "description": "Introduced species. Resident Rainbow Trout stay in lakes year-round. Steelhead are migratory rainbows that run up tributaries to spawn. Average 9-10 pounds for steelhead runs.",
        "visual_characteristics": "Silver body with pink-red stripe along lateral line. Black spots on back, dorsal fin, and tail. Steelhead returning from lake are bright silver.",
        "habitat": "Rainbow Trout: cool lakes and streams. Steelhead: open water of Great Lakes, enter tributaries spring and fall to spawn.",
        "size_range": "Rainbow Trout: 25-40 cm (10-16 inches), 1-3 pounds. Steelhead: 50-75 cm (20-30 inches), 5-15 pounds.",
        "distribution": "All Great Lakes, tributaries. Stocked in many inland lakes and rivers throughout Ontario.",
        "regulations": "Check Ontario fishing regulations. Tributary fishing may have catch-and-release or barbless hook requirements."
    },
    {
        "common_name": "Brown Trout",
        "scientific_name": "Salmo trutta",
        "family": "Salmonidae (Salmon Family)",
        "native": False,
        "description": "Introduced from Europe. Excellent sportfish known for wariness and difficulty to catch. Self-sustaining populations in many Great Lakes tributaries.",
        "visual_characteristics": "Brown to olive-brown back with golden-yellow sides. Red and black spots with pale halos. Few or no spots on tail. Adipose fin often has orange edge.",
        "habitat": "Cool streams and rivers, coastal areas of Great Lakes. More tolerant of warm water than Brook Trout or Rainbow Trout.",
        "size_range": "Typical: 30-50 cm (12-20 inches), 1-4 pounds. Trophy fish can exceed 75 cm (30 inches) and 15 pounds.",
        "distribution": "Great Lakes and tributaries, especially Lake Ontario and Lake Huron. Many Southern Ontario streams.",
        "regulations": "Check Ontario fishing regulations. Some streams have special regulations to protect wild trout."
    },
    {
        "common_name": "Brook Trout",
        "scientific_name": "Salvelinus fontinalis",
        "family": "Salmonidae (Salmon Family)",
        "native": True,
        "description": "Native char species (not a true trout). Requires cold, clean water with high oxygen. Indicator species for water quality. Ontario's provincial fish.",
        "visual_characteristics": "Dark olive-green back with distinctive worm-like markings (vermiculations) on back and dorsal fin. Red spots with blue halos on sides. White leading edges on lower fins with black stripe behind.",
        "habitat": "Cold headwater streams, spring-fed ponds, and lakes. Requires water temperature below 68°F. First species to disappear when water quality declines.",
        "size_range": "Stream fish: 15-25 cm (6-10 inches). Lake populations: can reach 40 cm (16 inches) and 3 pounds.",
        "distribution": "Tributaries of all Great Lakes, cold streams and lakes throughout Ontario. Stocked in many waters.",
        "regulations": "Check Ontario fishing regulations. Many streams have catch-and-release or barbless hook requirements. Some streams closed to protect wild populations."
    },
    {
        "common_name": "Channel Catfish",
        "scientific_name": "Ictalurus punctatus",
        "family": "Ictaluridae (Catfish Family)",
        "native": True,
        "description": "Found in all Great Lakes except Superior. Strong fighter and excellent eating. Most active at night and in murky water conditions.",
        "visual_characteristics": "Blue-grey to olive-grey on back, white to silver on belly. Black spots on sides (fade or disappear in large adults). Deeply forked tail. 4 pairs of barbels (whiskers).",
        "habitat": "Deep pools, river channels, around submerged structures. Prefers moderate current. Feeds primarily on bottom.",
        "size_range": "Typical: 30-60 cm (12-24 inches), 2-8 pounds. Trophy fish can exceed 90 cm (36 inches) and 20 pounds.",
        "distribution": "Lakes Erie, Huron, Michigan, Ontario. Many rivers and lakes in Southern Ontario.",
        "regulations": "Check Ontario fishing regulations. Generally liberal limits."
    },
    {
        "common_name": "Rock Bass",
        "scientific_name": "Ambloplites rupestris",
        "family": "Centrarchidae (Sunfish Family)",
        "native": True,
        "description": "Native and common throughout Great Lakes region. Often caught while fishing for other species. Provides good fishing for children and beginners.",
        "visual_characteristics": "Brassy-brown to olive coloring with dark brown blotches forming broken horizontal lines. Red eye is distinctive. 5-6 anal fin spines (Smallmouth Bass has 3).",
        "habitat": "Rocky areas, around boulders, submerged logs, and bridge pilings. Prefers clear water with moderate vegetation.",
        "size_range": "Typical: 15-25 cm (6-10 inches), 0.25-0.5 pounds. Can reach 30 cm (12 inches) and 1 pound.",
        "distribution": "All Great Lakes, Lake Simcoe, rivers and lakes throughout Ontario. One of the most common species.",
        "regulations": "Check Ontario fishing regulations. Generally liberal limits."
    },
    {
        "common_name": "Pumpkinseed",
        "scientific_name": "Lepomis gibbosus",
        "family": "Centrarchidae (Sunfish Family)",
        "native": True,
        "description": "Native, colorful panfish common throughout Ontario. Excellent species for teaching children to fish. Provides good ice fishing opportunities.",
        "visual_characteristics": "Orange, blue, and green coloring with wavy blue lines on cheek. Black gill cover flap with bright red-orange spot on tip. Deep-bodied and laterally compressed.",
        "habitat": "Shallow weedy areas, around docks and submerged vegetation. Prefers clear water with aquatic plants.",
        "size_range": "Typical: 10-18 cm (4-7 inches). Trophy fish can reach 25 cm (10 inches).",
        "distribution": "All Great Lakes, Lake Simcoe, ponds and lakes throughout Ontario. One of the most widespread panfish.",
        "regulations": "Check Ontario fishing regulations. Generally liberal limits."
    },
    {
        "common_name": "White Bass",
        "scientific_name": "Morone chrysops",
        "family": "Moronidae (Temperate Bass Family)",
        "native": True,
        "description": "Native schooling fish in Great Lakes. Excellent fighter for its size. Forms large spawning runs in tributaries during spring.",
        "visual_characteristics": "Silver-white body with 5-7 distinct dark horizontal stripes along sides. Moderately compressed body. Lower jaw projects slightly beyond upper jaw.",
        "habitat": "Open water of Great Lakes, schooling over sandy or rocky bottom. Enters tributaries in spring to spawn. Most active near surface when feeding.",
        "size_range": "Typical: 25-35 cm (10-14 inches), 0.5-1.5 pounds. Can reach 40 cm (16 inches) and 3 pounds.",
        "distribution": "All Great Lakes, particularly Lakes Erie and Ontario. Some inland lakes.",
        "regulations": "Check Ontario fishing regulations. Open season year-round in most waters."
    },
    {
        "common_name": "Sauger",
        "scientific_name": "Sander canadensis",
        "family": "Percidae (Perch Family)",
        "native": True,
        "description": "Native species similar to walleye but smaller. Excellent table fare. Often caught while fishing for walleye.",
        "visual_characteristics": "Olive-brown to brassy coloring with dark blotches forming saddle patterns on back. No white tip on lower tail lobe (distinguishes from walleye). Dark spots on dorsal fin membranes.",
        "habitat": "Deeper water than walleye, over sand and gravel bottom. Most active in low-light conditions.",
        "size_range": "Typical: 25-40 cm (10-16 inches), 0.5-2 pounds. Can reach 50 cm (20 inches) and 4 pounds.",
        "distribution": "Lakes Erie, Huron, Ontario, and St. Clair. Several rivers in Southern Ontario.",
        "regulations": "Check Ontario fishing regulations. Often combined bag limit with walleye."
    }
]

def create_species_pdf(species_data, output_dir):
    """Create PDF for a single fish species"""

    # Sanitize filename
    filename = species_data['common_name'].replace(' ', '_').replace('/', '_') + '.pdf'
    filepath = output_dir / filename

    # Create PDF document
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Build content
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=12,
        alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='darkgreen',
        italic=True,
        spaceAfter=6,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='darkblue',
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_LEFT
    )

    # Title
    story.append(Paragraph(species_data['common_name'], title_style))
    story.append(Paragraph(f"<i>{species_data['scientific_name']}</i>", subtitle_style))

    # Native status
    native_text = "NATIVE SPECIES" if species_data['native'] else "INTRODUCED SPECIES"
    story.append(Paragraph(f"<b>{native_text}</b>", subtitle_style))
    story.append(Spacer(1, 0.2*inch))

    # Family
    story.append(Paragraph(f"<b>Family:</b> {species_data['family']}", body_style))
    story.append(Spacer(1, 0.1*inch))

    # Description
    story.append(Paragraph("<b>Description:</b>", heading_style))
    story.append(Paragraph(species_data['description'], body_style))

    # Visual Characteristics
    story.append(Paragraph("<b>Visual Characteristics:</b>", heading_style))
    story.append(Paragraph(species_data['visual_characteristics'], body_style))

    # Habitat
    story.append(Paragraph("<b>Habitat:</b>", heading_style))
    story.append(Paragraph(species_data['habitat'], body_style))

    # Size Range
    story.append(Paragraph("<b>Size Range:</b>", heading_style))
    story.append(Paragraph(species_data['size_range'], body_style))

    # Distribution
    story.append(Paragraph("<b>Distribution:</b>", heading_style))
    story.append(Paragraph(species_data['distribution'], body_style))

    # Regulations
    story.append(Paragraph("<b>Fishing Regulations:</b>", heading_style))
    story.append(Paragraph(species_data['regulations'], body_style))

    # Footer
    story.append(Spacer(1, 0.3*inch))
    footer_text = "d3kOS Fish Species Database - Great Lakes & Lake Simcoe Region"
    story.append(Paragraph(f"<i>{footer_text}</i>",
                          ParagraphStyle('Footer', parent=styles['Normal'],
                                       fontSize=9, textColor='grey', alignment=TA_CENTER)))

    # Build PDF
    doc.build(story)
    print(f"✓ Created: {filename}")
    return filepath


def main():
    """Create PDFs for all fish species"""

    # Output directory
    output_dir = Path("/opt/d3kos/datasets/fish-rag/species_pdfs")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CREATING FISH SPECIES PDFs FOR RAG")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Total species: {len(FISH_SPECIES)}")
    print("")

    created_files = []

    for i, species in enumerate(FISH_SPECIES, 1):
        print(f"[{i}/{len(FISH_SPECIES)}] Creating {species['common_name']}...", flush=True)
        try:
            filepath = create_species_pdf(species, output_dir)
            created_files.append(filepath)
        except Exception as e:
            print(f"✗ Error creating {species['common_name']}: {e}")

    print("")
    print("=" * 60)
    print(f"✓ COMPLETE: Created {len(created_files)} species PDFs")
    print("=" * 60)
    print(f"Location: {output_dir}")
    print("")
    print("Next step: Add PDFs to RAG database")
    print(f"Command: cd /opt/d3kos/services/documents && python3 -c \"")
    print(f"from pdf_processor import PDFProcessor")
    print(f"import os")
    print(f"processor = PDFProcessor()")
    print(f"for pdf in sorted(os.listdir('{output_dir}')):")
    print(f"    if pdf.endswith('.pdf'):")
    print(f"        processor.add_document(os.path.join('{output_dir}', pdf))\"")

    return len(created_files)


if __name__ == "__main__":
    try:
        count = main()
        sys.exit(0 if count > 0 else 1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
