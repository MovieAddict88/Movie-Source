# CineCraze GitHub Workflow - Improved Version

## Overview

This repository now includes an improved GitHub Actions workflow that automatically handles large zip file uploads and creates pull requests. The workflow addresses the previous issues with large files (>10MB) and pull request creation failures.

## How It Works

### 1. **Upload Process**
- **ZIP Upload**: When you upload a `playlist.json.zip` file to any branch starting with `upload-*`, the workflow automatically triggers
- **Direct Upload**: For smaller files, you can still upload directly to main branch or create branches manually

### 2. **Automated Workflow**
The workflow (`unzip-playlist.yml`) automatically:
1. ✅ Checks out the repository
2. ✅ Validates the zip file exists
3. ✅ Installs 7zip for efficient extraction
4. ✅ Extracts `playlist.json` from the zip
5. ✅ Validates the extracted JSON file
6. ✅ Commits the extracted file
7. ✅ Creates a pull request automatically
8. ✅ Provides status updates

### 3. **Branch Naming Convention**
- **Upload branches**: Must start with `upload-` (e.g., `upload-2024-01-15-1430`)
- **Main branch**: Default is `main`
- **Workflow trigger**: Only activates on `upload-*` branches

## Usage Instructions

### **Option 1: ZIP Upload (Recommended for Large Files)**

1. **Prepare your data**:
   - Create a zip file containing `playlist.json`
   - Name it `playlist.json.zip`

2. **Upload via CineCraze**:
   - Set branch name to `upload-YYYY-MM-DD-HHMM` (e.g., `upload-2024-01-15-1430`)
   - Enable "Upload as ZIP" option
   - Click "Upload to GitHub"

3. **Workflow automatically**:
   - Extracts your file
   - Creates a pull request
   - You can then merge the PR

### **Option 2: Direct Upload (Small Files)**

1. **Upload directly to main**:
   - Set upload method to "Direct to Main Branch"
   - Disable ZIP option
   - Upload your `playlist.json` file

### **Option 3: Manual Branch + PR**

1. **Create branch**:
   - Set branch name (e.g., `feature-update-2024-01-15`)
   - Upload your file
   - Create PR manually

## Configuration

### **GitHub Settings**
```javascript
const GITHUB_CONFIG = {
    owner: 'YourUsername',
    repo: 'YourRepository',
    baseBranch: 'main',
    useZip: true,           // Enable for large files
    createPR: true,         // Auto-create PRs
    autoMerge: false        // Auto-merge (requires admin)
};
```

### **Workflow Configuration**
- **Timeout**: 30 minutes (increased for large files)
- **Triggers**: Push to `upload-*` branches with `playlist.json.zip`
- **Manual trigger**: Available via GitHub Actions UI

## Troubleshooting

### **Large File Issues (>10MB)**

**Problem**: Upload timeouts or failures
**Solutions**:
1. ✅ Use ZIP compression (reduces size by 60-80%)
2. ✅ Upload to `upload-*` branch (triggers workflow)
3. ✅ Check file size before upload
4. ✅ Use stable internet connection

### **Pull Request Creation Failures**

**Problem**: PR not created automatically
**Solutions**:
1. ✅ Ensure branch name starts with `upload-`
2. ✅ Check workflow status in Actions tab
3. ✅ Verify GitHub token has `repo` scope
4. ✅ Check repository permissions

### **Workflow Failures**

**Problem**: Workflow fails to run
**Solutions**:
1. ✅ Verify branch name format: `upload-YYYY-MM-DD-HHMM`
2. ✅ Check file path: `playlist.json.zip`
3. ✅ Ensure file is actually a valid zip
4. ✅ Check Actions tab for error details

## File Size Guidelines

| File Size | Recommended Method | Notes |
|-----------|-------------------|-------|
| < 5MB | Direct upload | Fast, immediate |
| 5-20MB | ZIP upload | Good compression |
| 20-50MB | ZIP upload | Required for reliability |
| > 50MB | ZIP upload | May take several minutes |

## Monitoring

### **Check Workflow Status**
1. Go to your repository's **Actions** tab
2. Look for "Unzip playlist.json.zip" workflow
3. Check the latest run status

### **Check Pull Requests**
1. Go to your repository's **Pull requests** tab
2. Look for auto-created PRs from workflow
3. Review and merge as needed

## Best Practices

1. **Always use ZIP for files >10MB**
2. **Use descriptive branch names**: `upload-2024-01-15-1430`
3. **Monitor workflow progress** in Actions tab
4. **Review PRs before merging**
5. **Keep main branch clean** - use branches for uploads

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Upload timed out" | File too large | Use ZIP compression |
| "Workflow not triggered" | Wrong branch name | Use `upload-*` format |
| "PR creation failed" | Permission issues | Check token scope |
| "Extraction failed" | Corrupted zip | Recreate zip file |

## Support

If you encounter issues:
1. Check the Actions tab for workflow errors
2. Verify your GitHub token permissions
3. Ensure branch naming follows convention
4. Check file size and format

---

**Note**: This workflow is designed to handle the specific use case of updating `playlist.json` files. For other file types, you may need to modify the workflow accordingly.