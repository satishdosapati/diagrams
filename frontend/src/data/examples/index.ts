import { awsExamples } from './aws'
import { azureExamples } from './azure'
import { gcpExamples } from './gcp'
import { Example, ExamplesByProvider } from './types'

export const examples: ExamplesByProvider = {
  aws: awsExamples,
  azure: azureExamples,
  gcp: gcpExamples
}

export function getExamplesByProvider(provider: "aws" | "azure" | "gcp"): Example[] {
  return examples[provider] || []
}

export function getExampleById(provider: "aws" | "azure" | "gcp", id: string): Example | undefined {
  return examples[provider]?.find(ex => ex.id === id)
}

export function getExamplesByCategory(provider: "aws" | "azure" | "gcp", category: string): Example[] {
  return examples[provider]?.filter(ex => ex.category === category) || []
}

// Re-export types for convenience
export type { Example, ExamplesByProvider } from './types'

