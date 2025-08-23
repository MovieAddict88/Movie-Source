# CineCraze GitHub Workflow Guide

## Overview

This repository uses GitHub Actions workflows to automatically process uploaded `playlist.json.zip` files and create pull requests for merging changes to the main branch.

## How It Works

### 1. Upload Process
1. **User uploads** `playlist.json.zip` to an `upload-*` branch
2. **Workflow triggers** automatically when the zip file is pushed
3. **File processing**:
   - Extracts the zip file
   - Validates JSON structure
   - Commits the extracted `playlist.json`
4. **Pull Request creation**:
   - Creates PR from upload branch to main branch
   - Adds automated comments and guidance

### 2. Workflow Files

#### Main Workflow: `unzip-playlist.yml`
- **Triggers**: Push to `upload-*` branches with `playlist.json.zip`
- **Actions**: Unzip, validate, commit, create PR
- **Timeout**: 30 minutes for large files
- **Permissions**: `contents:write`, `pull-requests:write`

#### Fallback Workflow: `create-pr-fallback.yml`
- **Triggers**: Main workflow completion or manual dispatch
- **Actions**: Create PR if main workflow fails
- **Timeout**: 15 minutes
- **Use case**: Backup when main workflow encounters issues

## File Size Guidelines

### Recommended Limits
- **< 10MB**: Direct upload (JSON)
- **10-100MB**: ZIP compression recommended
- **> 100MB**: Not supported by GitHub

### Automatic ZIP Detection
The application automatically enables ZIP compression for files larger than 10MB to improve upload performance.

## Troubleshooting Common Issues

### 1. Upload Fails (>10MB files)

**Symptoms**: Upload times out or fails with large files

**Solutions**:
- ✅ Enable ZIP compression in the app
- ✅ Check your internet connection stability
- ✅ Use smaller chunks if possible
- ✅ Verify GitHub token has sufficient permissions

**Error Messages**:
```
❌ Upload timed out after multiple attempts
❌ GitHub upload failed: Request timeout
```

### 2. Pull Request Not Created

**Symptoms**: File uploaded but no PR appears

**Solutions**:
- ✅ Check the Actions tab for workflow status
- ✅ Verify the branch name starts with `upload-`
- ✅ Check workflow logs for errors
- ✅ Use the fallback workflow if needed

**Manual PR Creation**:
```bash
# If workflows fail, create PR manually
gh pr create --head upload-your-branch --base main --title "Update playlist.json"
```

### 3. Workflow Fails

**Symptoms**: Workflow shows ❌ status

**Common Causes**:
- **JSON Validation Failed**: Invalid JSON structure in zip
- **Permission Denied**: Insufficient repository permissions
- **Branch Issues**: Source/target branch problems
- **File Size**: Exceeds GitHub limits

**Debugging Steps**:
1. Check workflow logs in Actions tab
2. Verify file structure and JSON validity
3. Check repository permissions
4. Ensure branch naming follows `upload-*` pattern

### 4. Large File Processing Issues

**Symptoms**: Timeout or memory errors with large files

**Solutions**:
- ✅ Use ZIP compression (automatically enabled for >10MB)
- ✅ Check workflow timeout settings (currently 30 minutes)
- ✅ Monitor workflow progress in Actions tab
- ✅ Consider splitting very large datasets

## Best Practices

### 1. Branch Naming
- Use format: `upload-YYYY-MM-DD-HHMM`
- Example: `upload-2024-01-15-1430`

### 2. File Preparation
- Ensure JSON is valid before zipping
- Use descriptive commit messages
- Test with smaller files first

### 3. Monitoring
- Check Actions tab after upload
- Monitor workflow progress
- Review PR details before merging

## Manual Workflow Triggers

### Trigger Main Workflow
```bash
# Push zip file to trigger workflow
git add playlist.json.zip
git commit -m "Upload playlist update"
git push origin upload-your-branch
```

### Trigger Fallback Workflow
```bash
# Manual trigger via GitHub UI
# Go to Actions > Create PR Fallback > Run workflow
# Or use GitHub CLI:
gh workflow run create-pr-fallback.yml -f source_branch=upload-your-branch
```

## Configuration

### Repository Settings
- **Branch Protection**: Main branch should be protected
- **Required Reviews**: Enable for main branch merges
- **Workflow Permissions**: Grant Actions read/write access

### GitHub Token Permissions
Required scopes:
- `repo` (full repository access)
- `workflow` (workflow management)
- `write:packages` (if using packages)

## Support

### Getting Help
1. **Check workflow logs** in Actions tab
2. **Review error messages** in the application
3. **Verify file structure** and JSON validity
4. **Check repository permissions** and settings

### Common Error Codes
- **401**: Unauthorized - Check token permissions
- **403**: Forbidden - Insufficient repository access
- **422**: Validation failed - Check file format
- **500**: Server error - Try again later

### File Structure Requirements
```json
{
  "Categories": [
    {
      "MainCategory": "Movies",
      "Entries": [...]
    },
    {
      "MainCategory": "TV Series", 
      "Entries": [...]
    }
  ]
}
```

## Performance Tips

### For Large Files (>10MB)
- ✅ Use ZIP compression
- ✅ Upload during off-peak hours
- ✅ Ensure stable internet connection
- ✅ Monitor workflow progress

### For Frequent Updates
- ✅ Use descriptive branch names
- ✅ Clean up old upload branches
- ✅ Monitor workflow queue
- ✅ Use manual triggers if needed

---

**Note**: This workflow is designed to handle files up to 100MB. For larger files, consider splitting the data or using external storage solutions.