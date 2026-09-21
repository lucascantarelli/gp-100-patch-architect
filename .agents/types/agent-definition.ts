/**
 * AgentDefinition — tipos do SDK Codebuff/Freebuff.
 * Gerado a partir da documentação oficial (codebuff.com/docs — AgentDefinition).
 * Import type-only: './types/agent-definition'
 */
export type ToolName =
  | 'read_files'
  | 'write_file'
  | 'str_replace'
  | 'apply_patch'
  | 'code_search'
  | 'find_files'
  | 'glob'
  | 'list_directory'
  | 'read_subtree'
  | 'run_terminal_command'
  | 'spawn_agents'
  | 'set_output'
  | 'end_turn'
  | 'ask_user'
  | 'suggest_followups'
  | 'write_todos'
  | 'web_search'
  | 'read_docs'
  | 'skill'

export interface JsonObjectSchema {
  type: 'object'
  properties?: Record<string, any>
  required?: string[]
  [key: string]: any
}

export interface InputSchema {
  prompt?: { type: 'string'; description?: string }
  params?: JsonObjectSchema
}

export interface MCPConfig {
  command: string
  args?: string[]
  env?: Record<string, string>
}

export interface ToolCallInput {
  [toolName: string]: any
}

export interface ToolCall {
  toolName: string
  input: ToolCallInput
  includeToolCall?: boolean
}

export interface AgentStepContext {
  agentState: any
  prompt?: string
  params?: Record<string, any>
  logger: {
    debug: (obj?: any, msg?: string) => void
    info: (obj?: any, msg?: string) => void
    warn: (obj?: any, msg?: string) => void
    error: (obj?: any, msg?: string) => void
  }
}

export type StepText = { type: 'STEP_TEXT'; text: string }
export type GenerateN = { type: 'GENERATE_N'; n: number }
export type StepCommand = 'STEP' | 'STEP_ALL' | StepText | GenerateN

export type YieldResult = {
  agentState: any
  toolResult: Array<{ type: string; value?: any }> | undefined
  stepsComplete: boolean
  nResponses?: string[]
}

export interface AgentDefinition {
  /** Unique id: lowercase letters, numbers, hyphens only */
  id: string
  version?: string
  publisher?: string
  /** Human-readable name shown in UI */
  displayName: string
  /** Any OpenRouter model string, e.g. 'z-ai/glm-5.3-flash' */
  model: string
  reasoningOptions?: {
    enabled?: boolean
    exclude?: boolean
  } & ({ max_tokens: number } | { effort: 'high' | 'medium' | 'low' | 'minimal' | 'none' })
  providerOptions?: Record<string, any>
  mcpServers?: Record<string, MCPConfig>
  /** Tools this agent can use */
  toolNames?: (ToolName | string)[]
  /** Other agents this agent can spawn */
  spawnableAgents?: string[]
  inputSchema?: InputSchema
  outputMode?: 'last_message' | 'all_messages' | 'structured_output'
  outputSchema?: JsonObjectSchema
  /** Prompt describing when/why to spawn this agent (for subagent use) */
  spawnerPrompt?: string
  /** Include parent conversation history */
  includeMessageHistory?: boolean
  /** Inherit parent system prompt (cannot combine with systemPrompt) */
  inheritParentSystemPrompt?: boolean
  /** Background context (prefer instructionsPrompt) */
  systemPrompt?: string
  /** Main instructions — most important behavior shaping prompt */
  instructionsPrompt?: string
  /** Prompt inserted at each step (usually not needed) */
  stepPrompt?: string
  /** Programmatic step control */
  handleSteps?: (context: AgentStepContext) => Generator<ToolCall | StepCommand | StepText, void, YieldResult>
}
