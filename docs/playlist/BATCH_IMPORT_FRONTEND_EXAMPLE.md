# 前端集成示例

## Vue 3 组件示例

```vue
<template>
  <div class="batch-import">
    <h3>批量导入音频文件</h3>
    
    <!-- 环境提示 -->
    <div class="environment-info">
      <span class="badge" :class="isDocker ? 'badge-docker' : 'badge-local'">
        {{ isDocker ? 'Docker模式' : '本地模式' }}
      </span>
    </div>

    <!-- Docker模式：目录选择器 -->
    <div v-if="isDocker" class="directory-selector">
      <label>选择目录：</label>
      <select v-model="selectedDirectory" class="form-select">
        <option value="">-- 请选择目录 --</option>
        <option 
          v-for="dir in availableDirectories" 
          :key="dir.path" 
          :value="dir.path"
        >
          {{ dir.name }}
        </option>
      </select>
    </div>

    <!-- 本地模式：文件选择器 -->
    <div v-else class="file-selector">
      <label>选择目录：</label>
      <input 
        type="text" 
        v-model="selectedDirectory" 
        placeholder="输入目录路径，如：/Users/username/Music"
        class="form-input"
      />
      <p class="hint">或使用系统文件选择器（需要Electron环境）</p>
    </div>

    <!-- 导入选项 -->
    <div class="import-options">
      <label>
        <input type="checkbox" v-model="recursive" />
        递归扫描子目录
      </label>
      
      <div class="file-extensions">
        <label>文件格式：</label>
        <div class="checkbox-group">
          <label v-for="ext in allExtensions" :key="ext">
            <input 
              type="checkbox" 
              :value="ext" 
              v-model="selectedExtensions"
            />
            {{ ext }}
          </label>
        </div>
      </div>
    </div>

    <!-- 导入按钮 -->
    <button 
      @click="startImport" 
      :disabled="!selectedDirectory || importing"
      class="btn-primary"
    >
      {{ importing ? '导入中...' : '开始导入' }}
    </button>

    <!-- 进度显示 -->
    <div v-if="importing" class="progress">
      <div class="spinner"></div>
      <span>正在扫描和导入文件...</span>
    </div>

    <!-- 结果显示 -->
    <div v-if="importResult" class="result">
      <h4>导入完成</h4>
      <ul>
        <li>成功导入：{{ importResult.imported }} 个文件</li>
        <li>跳过：{{ importResult.skipped }} 个文件</li>
        <li>扫描总数：{{ importResult.total_scanned }} 个文件</li>
        <li>播单总数：{{ importResult.playlist_total_items }} 首</li>
      </ul>
      
      <div v-if="importResult.skipped_files?.length" class="skipped-files">
        <p>部分文件被跳过：</p>
        <ul>
          <li v-for="file in importResult.skipped_files" :key="file">
            {{ file }}
          </li>
        </ul>
      </div>
    </div>

    <!-- 错误显示 -->
    <div v-if="error" class="error">
      <strong>错误：</strong>{{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const playlistId = route.params.id as string;

// 状态
const isDocker = ref(false);
const availableDirectories = ref<Array<{path: string, name: string}>>([]);
const selectedDirectory = ref('');
const recursive = ref(true);
const allExtensions = ['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac'];
const selectedExtensions = ref([...allExtensions]);
const importing = ref(false);
const importResult = ref<any>(null);
const error = ref('');

// 加载可用目录
async function loadDirectories() {
  try {
    const response = await fetch('/api/playlists/directories');
    const data = await response.json();
    
    isDocker.value = data.is_docker;
    availableDirectories.value = data.directories;
    
    // Docker模式下，默认选择第一个非根目录
    if (isDocker.value && data.directories.length > 1) {
      selectedDirectory.value = data.directories[1].path;
    }
  } catch (err) {
    error.value = '加载目录列表失败：' + err.message;
  }
}

// 开始导入
async function startImport() {
  if (!selectedDirectory.value) {
    error.value = '请选择目录';
    return;
  }

  importing.value = true;
  error.value = '';
  importResult.value = null;

  try {
    const response = await fetch(`/api/playlists/${playlistId}/import`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        directory: selectedDirectory.value,
        recursive: recursive.value,
        file_extensions: selectedExtensions.value,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '导入失败');
    }

    importResult.value = await response.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    importing.value = false;
  }
}

onMounted(() => {
  loadDirectories();
});
</script>

<style scoped>
.batch-import {
  padding: 20px;
  max-width: 600px;
}

.environment-info {
  margin-bottom: 20px;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-docker {
  background: #0066cc;
  color: white;
}

.badge-local {
  background: #28a745;
  color: white;
}

.directory-selector,
.file-selector {
  margin-bottom: 20px;
}

.form-select,
.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 8px;
}

.hint {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.import-options {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
}

.btn-primary {
  padding: 10px 24px;
  background: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
  padding: 15px;
  background: #e3f2fd;
  border-radius: 4px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #0066cc;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.result {
  margin-top: 20px;
  padding: 15px;
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
}

.result h4 {
  margin-top: 0;
  color: #155724;
}

.result ul {
  margin: 10px 0;
  padding-left: 20px;
}

.skipped-files {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #c3e6cb;
}

.error {
  margin-top: 20px;
  padding: 15px;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  color: #721c24;
}
</style>
```

## React 组件示例

```tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

interface Directory {
  path: string;
  name: string;
  is_docker: boolean;
}

interface ImportResult {
  imported: number;
  skipped: number;
  total_scanned: number;
  playlist_total_items: number;
  skipped_files?: string[];
}

export const BatchImport: React.FC = () => {
  const { playlistId } = useParams<{ playlistId: string }>();
  
  const [isDocker, setIsDocker] = useState(false);
  const [directories, setDirectories] = useState<Directory[]>([]);
  const [selectedDirectory, setSelectedDirectory] = useState('');
  const [recursive, setRecursive] = useState(true);
  const [selectedExtensions, setSelectedExtensions] = useState([
    '.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac'
  ]);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDirectories();
  }, []);

  const loadDirectories = async () => {
    try {
      const response = await fetch('/api/playlists/directories');
      const data = await response.json();
      
      setIsDocker(data.is_docker);
      setDirectories(data.directories);
      
      if (data.is_docker && data.directories.length > 1) {
        setSelectedDirectory(data.directories[1].path);
      }
    } catch (err) {
      setError('加载目录列表失败：' + (err as Error).message);
    }
  };

  const handleImport = async () => {
    if (!selectedDirectory) {
      setError('请选择目录');
      return;
    }

    setImporting(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`/api/playlists/${playlistId}/import`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          directory: selectedDirectory,
          recursive,
          file_extensions: selectedExtensions,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '导入失败');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setImporting(false);
    }
  };

  const toggleExtension = (ext: string) => {
    setSelectedExtensions(prev =>
      prev.includes(ext)
        ? prev.filter(e => e !== ext)
        : [...prev, ext]
    );
  };

  return (
    <div className="batch-import">
      <h3>批量导入音频文件</h3>
      
      <div className="environment-info">
        <span className={`badge ${isDocker ? 'badge-docker' : 'badge-local'}`}>
          {isDocker ? 'Docker模式' : '本地模式'}
        </span>
      </div>

      {isDocker ? (
        <div className="directory-selector">
          <label>选择目录：</label>
          <select 
            value={selectedDirectory}
            onChange={(e) => setSelectedDirectory(e.target.value)}
            className="form-select"
          >
            <option value="">-- 请选择目录 --</option>
            {directories.map(dir => (
              <option key={dir.path} value={dir.path}>
                {dir.name}
              </option>
            ))}
          </select>
        </div>
      ) : (
        <div className="file-selector">
          <label>选择目录：</label>
          <input
            type="text"
            value={selectedDirectory}
            onChange={(e) => setSelectedDirectory(e.target.value)}
            placeholder="输入目录路径，如：/Users/username/Music"
            className="form-input"
          />
          <p className="hint">或使用系统文件选择器（需要Electron环境）</p>
        </div>
      )}

      <div className="import-options">
        <label>
          <input
            type="checkbox"
            checked={recursive}
            onChange={(e) => setRecursive(e.target.checked)}
          />
          递归扫描子目录
        </label>
        
        <div className="file-extensions">
          <label>文件格式：</label>
          <div className="checkbox-group">
            {['.mp3', '.m4a', '.flac', '.wav', '.ogg', '.aac'].map(ext => (
              <label key={ext}>
                <input
                  type="checkbox"
                  checked={selectedExtensions.includes(ext)}
                  onChange={() => toggleExtension(ext)}
                />
                {ext}
              </label>
            ))}
          </div>
        </div>
      </div>

      <button
        onClick={handleImport}
        disabled={!selectedDirectory || importing}
        className="btn-primary"
      >
        {importing ? '导入中...' : '开始导入'}
      </button>

      {importing && (
        <div className="progress">
          <div className="spinner"></div>
          <span>正在扫描和导入文件...</span>
        </div>
      )}

      {result && (
        <div className="result">
          <h4>导入完成</h4>
          <ul>
            <li>成功导入：{result.imported} 个文件</li>
            <li>跳过：{result.skipped} 个文件</li>
            <li>扫描总数：{result.total_scanned} 个文件</li>
            <li>播单总数：{result.playlist_total_items} 首</li>
          </ul>
          
          {result.skipped_files && result.skipped_files.length > 0 && (
            <div className="skipped-files">
              <p>部分文件被跳过：</p>
              <ul>
                {result.skipped_files.map((file, index) => (
                  <li key={index}>{file}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="error">
          <strong>错误：</strong>{error}
        </div>
      )}
    </div>
  );
};
```

## Electron 文件选择器集成

```typescript
// 在 Electron 主进程中
import { dialog, ipcMain } from 'electron';

ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory']
  });
  
  if (result.canceled) {
    return null;
  }
  
  return result.filePaths[0];
});

// 在渲染进程中
const { ipcRenderer } = window.require('electron');

async function selectDirectory() {
  const directory = await ipcRenderer.invoke('select-directory');
  if (directory) {
    setSelectedDirectory(directory);
  }
}
```

## API调用封装

```typescript
// api/playlist.ts
export interface ImportRequest {
  directory: string;
  recursive?: boolean;
  file_extensions?: string[];
}

export interface ImportResult {
  imported: number;
  skipped: number;
  total_scanned: number;
  playlist_total_items: number;
  skipped_files?: string[];
}

export interface DirectoryInfo {
  path: string;
  name: string;
  is_docker: boolean;
}

export interface DirectoriesResponse {
  directories: DirectoryInfo[];
  is_docker: boolean;
  message: string;
}

export const playlistApi = {
  async getDirectories(): Promise<DirectoriesResponse> {
    const response = await fetch('/api/playlists/directories');
    if (!response.ok) throw new Error('Failed to load directories');
    return response.json();
  },

  async importFromDirectory(
    playlistId: string,
    request: ImportRequest
  ): Promise<ImportResult> {
    const response = await fetch(`/api/playlists/${playlistId}/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Import failed');
    }
    
    return response.json();
  },
};
```

## 使用建议

1. **错误处理**：提供清晰的错误提示
2. **进度反馈**：显示导入进度（可考虑WebSocket）
3. **结果展示**：清晰展示导入统计信息
4. **用户体验**：
   - Docker模式：提供目录下拉选择
   - 本地模式：提供文件选择器按钮
   - 显示环境标识，避免用户困惑
