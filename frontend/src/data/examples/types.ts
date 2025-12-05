export interface Example {
  id: string
  title: string
  description: string
  prompt: string
  codeSnippet: string
  category: string
  complexity: "simple" | "medium" | "complex"
  tags: string[]
  recommendedVariations?: string[]
}

export interface ExamplesByProvider {
  aws: Example[]
  azure: Example[]
  gcp: Example[]
}

