# Thumbs Up/Down Feedback System

## Overview

A self-improving feedback system that collects user feedback (thumbs up/down) and learns from successful patterns to improve future code generation.

## Implementation

### Backend Components

1. **Feedback Storage** (`backend/src/storage/feedback_storage.py`)
   - Stores feedback in JSON files (`data/feedback/feedback.json`)
   - Extracts patterns from thumbs up feedback
   - Stores patterns in `data/feedback/patterns.json`
   - Provides feedback statistics

2. **API Endpoints** (`backend/src/api/routes.py`)
   - `POST /api/feedback` - Submit thumbs up/down feedback
   - `GET /api/feedback/stats` - Get feedback statistics
   - Updated `POST /api/generate-diagram` to include `generation_id`

### Frontend Components

1. **FeedbackWidget** (`frontend/src/components/FeedbackWidget.tsx`)
   - Thumbs up/down buttons
   - Submits feedback to backend
   - Shows confirmation message after submission

2. **API Client** (`frontend/src/services/api.ts`)
   - `submitFeedback()` - Submit feedback
   - `getFeedbackStats()` - Get statistics
   - Updated `GenerateDiagramResponse` to include `generation_id`

3. **Integration** (`frontend/src/components/DiagramGenerator.tsx`)
   - Feedback widget displayed after diagram generation
   - Links feedback to generation_id and session_id

## How It Works

1. **User generates diagram** → System creates unique `generation_id`
2. **User sees diagram** → Feedback widget appears below diagram
3. **User clicks thumbs up/down** → Feedback submitted with:
   - `generation_id` (links to specific generation)
   - `session_id` (links to user session)
   - `code_hash` (SHA256 hash of generated code)
   - `code` (full code for pattern extraction)
4. **System processes feedback**:
   - **Thumbs up**: Extracts successful patterns (imports, structure)
   - **Thumbs down**: Records for future analysis
5. **Patterns stored** → Used to improve future generations

## Pattern Learning

When thumbs up feedback is received, the system extracts:

1. **Import Patterns**
   - Which imports work well together
   - Common import combinations

2. **Structure Patterns**
   - Component count
   - Connection count
   - Use of clusters
   - Use of edges

Patterns are stored with:
- Success rate (thumbs up count / total feedback)
- Usage frequency
- Pattern metadata

## Data Storage

- **Feedback**: `backend/data/feedback/feedback.json`
- **Patterns**: `backend/data/feedback/patterns.json`

Both files are created automatically on first use.

## Usage

### Submitting Feedback

```typescript
await submitFeedback({
  generation_id: "uuid",
  session_id: "uuid",
  thumbs_up: true,
  code_hash: "sha256_hash",
  code: "generated_python_code"
});
```

### Getting Statistics

```typescript
const stats = await getFeedbackStats(30); // Last 30 days
// Returns: { total_feedbacks, thumbs_up, thumbs_down, thumbs_up_rate }
```

## Future Enhancements

1. **Pattern Application**: Use learned patterns to improve code generation
2. **Anti-pattern Detection**: Learn from thumbs down to avoid problematic patterns
3. **Context-Aware Patterns**: Link patterns to specific scenarios (provider, diagram type)
4. **Pattern Evolution**: Update patterns as code improves
5. **Analytics Dashboard**: Visualize feedback trends and pattern success rates

## Configuration

The feedback system is enabled by default. Storage path can be configured via:

```python
feedback_storage = FeedbackStorage(storage_path="./data/feedback")
```

## Testing

1. Generate a diagram
2. Click thumbs up or thumbs down
3. Check `backend/data/feedback/feedback.json` for stored feedback
4. Check `backend/data/feedback/patterns.json` for extracted patterns (if thumbs up)
