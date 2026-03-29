<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            添加用户
          </el-button>
        </div>
      </template>
      
      <el-table :data="users" v-loading="loading">
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最近登录" width="180">
          <template #default="{ row }">
            {{ row.last_login ? formatDate(row.last_login) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button
              size="small"
              @click="showEditDialog(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.enabled"
              size="small"
              type="warning"
              :disabled="row.role === 'admin'"
              @click="handleDisable(row)"
            >
              禁用
            </el-button>
            <el-button
              v-else
              size="small"
              type="success"
              @click="handleEnable(row)"
            >
              启用
            </el-button>
            <el-button
              size="small"
              type="danger"
              :disabled="row.role === 'admin'"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '创建用户'"
      width="500px"
    >
      <el-form :model="userForm" :rules="formRules" ref="formRef" label-width="110px">
        <el-form-item v-if="!isEdit" label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名"
          />
        </el-form-item>
        
        <el-form-item v-if="isEdit" label="当前用户名">
          <el-input
            v-model="userForm.username"
            disabled
          />
        </el-form-item>
        
        <el-form-item v-if="isEdit" label="新用户名">
          <el-input
            v-model="userForm.newUsername"
            placeholder="留空则不修改用户名"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="userForm.password"
            type="password"
            :placeholder="isEdit ? '留空则不修改密码' : '请输入密码'"
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="isEdit" label="启用状态">
          <el-switch
            v-model="userForm.enabled"
            active-text="启用"
            inactive-text="禁用"
            :disabled="userForm.role === 'admin'"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { listUsers, createUser, updateUser, deleteUser, enableUser, disableUser } from '@/api/auth'

interface User {
  username: string
  role: string
  created_at: string
  last_login?: string
  enabled: boolean
}

const loading = ref(false)
const users = ref<User[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const userForm = reactive({
  username: '',
  newUsername: '',
  password: '',
  role: 'user',
  enabled: true
})

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    {
      validator: (rule: any, value: string, callback: any) => {
        if (!isEdit.value && !value) {
          callback(new Error('请输入密码'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const loadUsers = async () => {
  loading.value = true
  try {
    users.value = await listUsers()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  userForm.username = ''
  userForm.newUsername = ''
  userForm.password = ''
  userForm.role = 'user'
  userForm.enabled = true
  dialogVisible.value = true
}

const showEditDialog = (user: User) => {
  isEdit.value = true
  userForm.username = user.username
  userForm.newUsername = ''
  userForm.password = ''
  userForm.role = user.role
  userForm.enabled = user.enabled
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value) {
        // 前端额外检查：不允许禁用管理员
        if (userForm.role === 'admin' && userForm.enabled === false) {
          ElMessage.error('不能禁用管理员账户')
          submitting.value = false
          return
        }
        
        const currentUsername = localStorage.getItem('username')
        const isModifyingSelf = userForm.username === currentUsername
        const isChangingUsername = userForm.newUsername && userForm.newUsername !== userForm.username
        
        await updateUser(userForm.username, {
          new_username: userForm.newUsername || undefined,
          password: userForm.password || undefined,
          role: userForm.role,
          enabled: userForm.enabled
        })
        
        // 如果修改了自己的用户名，需要重新登录
        if (isModifyingSelf && isChangingUsername) {
          ElMessage.success('用户名修改成功，请重新登录')
          setTimeout(() => {
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            localStorage.removeItem('role')
            window.location.href = '/login'
          }, 1500)
          return
        }
        
        ElMessage.success('用户更新成功')
      } else {
        await createUser(userForm.username, userForm.password, userForm.role)
        ElMessage.success('用户创建成功')
      }
      
      dialogVisible.value = false
      await loadUsers()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 ${user.username} 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteUser(user.username)
    ElMessage.success('用户删除成功')
    await loadUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleEnable = async (user: User) => {
  try {
    await enableUser(user.username)
    ElMessage.success(`用户 ${user.username} 已启用`)
    await loadUsers()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '启用失败')
  }
}

const handleDisable = async (user: User) => {
  // 前端额外检查：不允许禁用管理员
  if (user.role === 'admin') {
    ElMessage.error('不能禁用管理员账户')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要禁用用户 ${user.username} 吗？禁用后该用户将无法登录。`,
      '确认禁用',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await disableUser(user.username)
    ElMessage.success(`用户 ${user.username} 已禁用`)
    await loadUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '禁用失败')
    }
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  /* padding 由 .main-content 提供 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
