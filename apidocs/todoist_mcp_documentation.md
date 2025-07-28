# Todoist MCP Server Documentation

## Overview

The Todoist MCP (Model Context Protocol) server provides a comprehensive interface for interacting with Todoist through AI assistants like Claude. It implements all APIs available from the Todoist TypeScript Client, enabling full task and project management capabilities.

## Installation & Setup

### Prerequisites
- Node.js installed on your system
- Todoist API key (obtain from [Todoist Settings > Integrations > Developer](https://app.todoist.com/app/settings/integrations/developer))
- Claude Desktop app or other MCP-compatible client

### For Claude Code

The Todoist MCP server is already configured in your project. To use it, ensure your environment has the `TODOIST_API_KEY` set.

### Configuration

Add to your Claude configuration:

```json
{
    "mcpServers": {
        "todoist-mcp": {
            "command": "node",
            "args": ["/path/to/mcp-servers/todoist-mcp/build/index.js"],
            "env": {
                "TODOIST_API_KEY": "your_todoist_api_key"
            }
        }
    }
}
```

## Available Tools

### Task Management

#### 1. **add-task** - Create a new task
```typescript
// Parameters:
{
  "content": "Task description",
  "description": "Detailed description",
  "projectId": "optional project ID",
  "sectionId": "optional section ID",
  "parentId": "optional parent task ID",
  "order": 1,
  "labels": ["label1", "label2"],
  "priority": 1-4,
  "dueString": "natural language date",
  "dueDate": "YYYY-MM-DD",
  "dueDatetime": "ISO datetime",
  "dueLang": "en",
  "assigneeId": "user ID",
  "duration": 60,
  "durationUnit": "minute"
}
```

#### 2. **quick-add-task** - Create task with natural language
```typescript
// Parameters:
{
  "text": "Submit report by Friday 5pm #Work @John",
  "autoReminder": true,
  "responsibleUid": "user ID"
}
```

#### 3. **get-task** - Retrieve a single task
```typescript
// Parameters:
{
  "id": "task_id"
}
```

#### 4. **get-tasks** - Get all active tasks
```typescript
// Parameters:
{
  "projectId": "optional project filter",
  "sectionId": "optional section filter",
  "label": "optional label filter",
  "filter": "optional filter query",
  "lang": "en",
  "ids": ["id1", "id2"]
}
```

#### 5. **get-tasks-by-filter** - Get tasks using Todoist filters
```typescript
// Parameters:
{
  "filter": "today | overdue | p1",
  "lang": "en"
}
```

#### 6. **update-task** - Modify an existing task
```typescript
// Parameters:
{
  "id": "task_id",
  "content": "Updated content",
  "description": "Updated description",
  "labels": ["new", "labels"],
  "priority": 1-4,
  "dueString": "new due date",
  "assigneeId": "new assignee"
}
```

#### 7. **close-task** - Complete a task
```typescript
// Parameters:
{
  "id": "task_id"
}
```

#### 8. **reopen-task** - Reopen a completed task
```typescript
// Parameters:
{
  "id": "task_id"
}
```

#### 9. **delete-task** - Permanently delete a task
```typescript
// Parameters:
{
  "id": "task_id"
}
```

#### 10. **move-tasks** - Move multiple tasks to a different project/section
```typescript
// Parameters:
{
  "ids": ["task1", "task2"],
  "projectId": "target_project",
  "sectionId": "target_section",
  "parentId": "new_parent_task"
}
```

### Completed Tasks

#### 11. **get-tasks-completed-by-completion-date** - Get tasks completed within a date range
```typescript
// Parameters:
{
  "since": "2024-01-01T00:00:00",
  "until": "2024-01-31T23:59:59",
  "projectId": "optional project filter",
  "sectionId": "optional section filter",
  "limit": 100,
  "offset": 0
}
```

#### 12. **get-tasks-completed-by-due-date** - Get tasks by their original due date
```typescript
// Parameters: same as above
```

### Project Management

#### 13. **add-project** - Create a new project
```typescript
// Parameters:
{
  "name": "Project Name",
  "parentId": "parent project ID",
  "color": "berry_red",
  "isFavorite": true,
  "viewStyle": "list"
}
```

#### 14. **get-project** - Retrieve project details
```typescript
// Parameters:
{
  "id": "project_id"
}
```

#### 15. **get-projects** - List all projects
```typescript
// No parameters required
```

#### 16. **update-project** - Modify project
```typescript
// Parameters:
{
  "id": "project_id",
  "name": "New Name",
  "color": "new_color",
  "isFavorite": true
}
```

#### 17. **delete-project** - Remove project
```typescript
// Parameters:
{
  "id": "project_id"
}
```

### Section Management

#### 18. **add-section** - Create a new section
```typescript
// Parameters:
{
  "name": "Section Name",
  "projectId": "parent_project_id",
  "order": 1
}
```

#### 19. **get-section** - Retrieve section details
```typescript
// Parameters:
{
  "id": "section_id"
}
```

#### 20. **get-sections** - List sections
```typescript
// Parameters:
{
  "projectId": "filter by project"
}
```

#### 21. **update-section** - Modify section
```typescript
// Parameters:
{
  "id": "section_id",
  "name": "New Name"
}
```

#### 22. **delete-section** - Remove section
```typescript
// Parameters:
{
  "id": "section_id"
}
```

### Comment Management

#### 23. **add-comment** - Add a comment
```typescript
// Parameters:
{
  "content": "Comment text",
  "taskId": "for task comments",
  "projectId": "for project comments",
  "attachment": {
    "fileName": "file.pdf",
    "fileType": "application/pdf",
    "fileUrl": "https://..."
  }
}
```

#### 24. **get-comment** - Retrieve a comment
```typescript
// Parameters:
{
  "id": "comment_id"
}
```

#### 25. **get-comments** - List all comments
```typescript
// Parameters:
{
  "projectId": "filter by project",
  "taskId": "filter by task"
}
```

#### 26. **update-comment** - Modify comment
```typescript
// Parameters:
{
  "id": "comment_id",
  "content": "Updated comment"
}
```

#### 27. **delete-comment** - Remove comment
```typescript
// Parameters:
{
  "id": "comment_id"
}
```

### Label Management

#### 28. **add-label** - Create a new label
```typescript
// Parameters:
{
  "name": "Label Name",
  "order": 1,
  "color": "red",
  "isFavorite": true
}
```

#### 29. **get-label** - Retrieve label details
```typescript
// Parameters:
{
  "id": "label_id"
}
```

#### 30. **get-labels** - List all personal labels
```typescript
// No parameters required
```

#### 31. **update-label** - Modify label
```typescript
// Parameters:
{
  "id": "label_id",
  "name": "New Name",
  "order": 2,
  "color": "blue"
}
```

#### 32. **delete-label** - Remove label
```typescript
// Parameters:
{
  "id": "label_id"
}
```

### Shared Labels

#### 33. **get-shared-labels** - List shared labels
```typescript
// No parameters required
```

#### 34. **rename-shared-label** - Rename a shared label
```typescript
// Parameters:
{
  "name": "current_name",
  "newName": "new_name"
}
```

#### 35. **remove-shared-label** - Remove a shared label
```typescript
// Parameters:
{
  "name": "label_name"
}
```

### Collaboration

#### 36. **get-project-collaborators** - List project members
```typescript
// Parameters:
{
  "projectId": "project_id"
}
```

### Statistics

#### 37. **get-productivity-stats** - Get user productivity statistics
```typescript
// No parameters required
// Returns: completed tasks count, daily/weekly goals, karma trends
```

## Usage Examples

### Example 1: Create a task with natural language
```javascript
// Using quick-add-task
{
  "tool": "quick-add-task",
  "arguments": {
    "text": "Review quarterly report tomorrow at 2pm #Work p1"
  }
}
```

### Example 2: Get today's tasks
```javascript
// Using get-tasks-by-filter
{
  "tool": "get-tasks-by-filter",
  "arguments": {
    "filter": "today"
  }
}
```

### Example 3: Complete a task
```javascript
// Using close-task
{
  "tool": "close-task",
  "arguments": {
    "id": "task_12345"
  }
}
```

### Example 4: Create a project with sections
```javascript
// First create project
{
  "tool": "add-project",
  "arguments": {
    "name": "Q1 Marketing Campaign",
    "color": "berry_red"
  }
}

// Then add sections
{
  "tool": "add-section",
  "arguments": {
    "name": "Planning",
    "projectId": "project_id_from_above"
  }
}
```

## Best Practices

1. **Natural Language Input**: Use `quick-add-task` for natural language task creation
2. **Batch Operations**: Use `move-tasks` for bulk task management
3. **Filtering**: Leverage Todoist's powerful filter syntax with `get-tasks-by-filter`
4. **Hierarchical Organization**: Utilize projects, sections, and subtasks for organization
5. **Labels**: Use labels for cross-project categorization
6. **Due Dates**: Can use natural language ("tomorrow at 5pm") or specific dates

## Error Handling

The MCP server will return appropriate error messages for:
- Invalid task/project/section IDs
- Missing required parameters
- API rate limiting
- Authentication failures

## Integration Tips

1. **Context Awareness**: The MCP server maintains no state between calls
2. **ID Management**: Store returned IDs for subsequent operations
3. **Bulk Operations**: Use batch endpoints when available for efficiency
4. **Natural Language**: Leverage Todoist's NLP for date parsing

## Common Workflows

### Daily Review
1. Get today's tasks: `get-tasks-by-filter` with filter "today"
2. Get overdue tasks: `get-tasks-by-filter` with filter "overdue"
3. Complete tasks: `close-task` for each completed item

### Weekly Planning
1. Create new project: `add-project`
2. Add sections: `add-section` for each phase
3. Add tasks: `quick-add-task` with natural language
4. Set priorities: `update-task` with priority levels

### Project Migration
1. Get all tasks from project: `get-tasks` with projectId
2. Create new project: `add-project`
3. Move tasks: `move-tasks` with new projectId