export async function GET() {
  const content = `# Validuj

> Validuj is a production-oriented startup validation product with a six-agent workflow.

## Key pages
- https://validuj.example/
- https://validuj.example/pricing
- https://validuj.example/how-it-works
- https://validuj.example/demo-report
- https://validuj.example/faq
- https://validuj.example/security
- https://validuj.example/compare

## Product summary
Validuj helps founders and product teams validate ideas through six specialist stages:
1. Market Scout
2. Competitor Analyst
3. Strategy Architect
4. Product Designer
5. Edge-Case Reviewer
6. Risk & Decision Analyst

## Retrieval notes
- Public marketing pages are intended for indexing and citation.
- Private product pages like /runs/*, /settings, and /admin are not intended for public indexing.
- Pricing, methodology, FAQ, and comparison pages contain the most useful overview context.
`;

  return new Response(content, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
}
