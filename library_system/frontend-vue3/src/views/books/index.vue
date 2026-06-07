<template>
  <div class="books-page">
    <!-- 工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <el-form :inline="true" class="toolbar-form">
        <el-form-item>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索书名、作者、ISBN..."
            clearable
            :prefix-icon="Search"
            @keyup.enter="handleSearch"
            style="width: 280px"
          />
        </el-form-item>
        <el-form-item>
          <el-select v-model="searchForm.category" placeholder="全部分类" clearable style="width: 140px">
            <el-option
              v-for="cat in categories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="searchForm.available_only">仅显示可借</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="resetSearch">重置</el-button>
        </el-form-item>
        <el-form-item v-if="userStore.isAdminOrLibrarian">
          <el-button type="success" :icon="Plus" @click="openAddDialog">添加图书</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图书卡片列表 -->
    <el-row :gutter="20" v-loading="loading">
      <el-col
        v-for="book in books"
        :key="book.id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
        :xl="4"
        class="book-col"
      >
        <el-card shadow="hover" class="book-card">
          <div class="book-cover-wrapper">
            <el-image
              :src="getCoverUrl(book.cover_image)"
              fit="cover"
              class="book-cover"
              :preview-src-list="book.cover_image ? [getCoverUrl(book.cover_image)] : []"
            >
              <template #error>
                <div class="cover-placeholder">
                  <el-icon :size="40"><Picture /></el-icon>
                  <div class="placeholder-text">暂无封面</div>
                </div>
              </template>
            </el-image>
            <div class="book-badge" v-if="book.available_copies === 0">
              <el-tag type="danger" effect="dark" size="small">已借完</el-tag>
            </div>
          </div>
          <div class="book-info">
            <div class="book-title" :title="book.title">{{ book.title }}</div>
            <div class="book-author">{{ book.author }}</div>
            <div class="book-meta">
              <el-tag size="small" v-if="book.category">{{ book.category }}</el-tag>
              <span class="book-stock" :class="book.available_copies > 0 ? 'in-stock' : 'out-stock'">
                库存 {{ book.available_copies }}/{{ book.total_copies }}
              </span>
            </div>
            <div class="book-location" v-if="book.location">
              <el-icon><Location /></el-icon> {{ book.location }}
            </div>
            <div class="book-actions">
              <el-button
                v-if="book.available_copies > 0"
                type="success"
                size="small"
                :icon="Handbag"
                @click="openBorrowDialog(book)"
              >借阅</el-button>
              <template v-if="userStore.isAdminOrLibrarian">
                <el-button type="primary" size="small" :icon="Edit" @click="openEditDialog(book)">编辑</el-button>
                <el-button type="danger" size="small" :icon="Delete" @click="handleDelete(book)">删除</el-button>
              </template>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <el-empty v-if="!loading && books.length === 0" description="暂无图书数据" />

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="books.length > 0">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑图书' : '添加图书'"
      width="650px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="ISBN" prop="isbn">
              <el-input v-model="form.isbn" placeholder="978-7-111-11111-1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="书名" prop="title">
              <el-input v-model="form.title" placeholder="请输入书名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="作者" prop="author">
              <el-input v-model="form.author" placeholder="请输入作者" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出版社">
              <el-input v-model="form.publisher" placeholder="请输入出版社" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出版年份">
              <el-input-number v-model="form.publish_year" :min="1000" :max="2100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-input v-model="form.category" placeholder="如：计算机" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="总数量" prop="total_copies">
              <el-input-number v-model="form.total_copies" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="书架位置">
              <el-input v-model="form.location" placeholder="如：A区-3排-2层" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="图书简介..." />
        </el-form-item>
        <el-form-item label="封面图片">
          <el-upload
            class="cover-uploader"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleCoverChange"
            accept="image/*"
          >
            <img v-if="coverPreview" :src="coverPreview" class="cover-preview" />
            <div v-else-if="form.cover_image" class="cover-preview-wrapper">
              <img :src="getCoverUrl(form.cover_image)" class="cover-preview" />
              <div class="cover-overlay">
                <el-icon><Edit /></el-icon>
                <div>更换封面</div>
              </div>
            </div>
            <div v-else class="cover-upload-trigger">
              <el-icon :size="28"><Plus /></el-icon>
              <div>点击上传封面</div>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 借阅弹窗 -->
    <el-dialog v-model="borrowDialogVisible" title="借阅图书" width="400px">
      <el-form :model="borrowForm" label-width="100px">
        <el-form-item label="图书">
          <el-input v-model="borrowForm.bookTitle" disabled />
        </el-form-item>
        <el-form-item label="借阅天数">
          <el-input-number v-model="borrowForm.days" :min="1" :max="90" style="width: 100%" />
          <div class="form-tip">最多可借 90 天</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="borrowLoading" @click="handleBorrow">确认借阅</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getBooks, searchBooks, createBook, updateBook, deleteBook, uploadCover } from '@/api/book'
import { borrowBook } from '@/api/borrow'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, Plus, Handbag, Edit, Delete, Picture, Location
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const loading = ref(false)
const books = ref([])
const categories = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = reactive({
  keyword: '',
  category: '',
  available_only: false
})

// 弹窗
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const submitting = ref(false)
const form = reactive({
  isbn: '',
  title: '',
  author: '',
  publisher: '',
  publish_year: null,
  category: '',
  total_copies: 1,
  location: '',
  description: '',
  cover_image: ''
})

const coverFile = ref(null)
const coverPreview = ref('')

const rules = {
  isbn: [{ required: true, message: '请输入ISBN', trigger: 'blur' }],
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  total_copies: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

// 借阅弹窗
const borrowDialogVisible = ref(false)
const borrowLoading = ref(false)
const borrowForm = reactive({
  bookId: null,
  bookTitle: '',
  days: 30
})

function getCoverUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return path
}

async function loadBooks() {
  loading.value = true
  try {
    const params = {
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.category) params.category = searchForm.category
    if (searchForm.available_only) params.available_only = true

    const res = await getBooks(params)
    books.value = res || []
    total.value = res?.length || 0

    const all = await getBooks({ limit: 100 })
    categories.value = [...new Set((all || []).map(b => b.category).filter(Boolean))]
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadBooks()
}

function resetSearch() {
  searchForm.keyword = ''
  searchForm.category = ''
  searchForm.available_only = false
  handleSearch()
}

function handleSizeChange(val) {
  pageSize.value = val
  loadBooks()
}

function handlePageChange(val) {
  page.value = val
  loadBooks()
}

function openAddDialog() {
  isEdit.value = false
  Object.assign(form, {
    isbn: '', title: '', author: '', publisher: '',
    publish_year: null, category: '', total_copies: 1,
    location: '', description: '', cover_image: ''
  })
  coverFile.value = null
  coverPreview.value = ''
  dialogVisible.value = true
}

function openEditDialog(row) {
  isEdit.value = true
  Object.assign(form, { ...row })
  coverFile.value = null
  coverPreview.value = ''
  dialogVisible.value = true
}

function handleCoverChange(file) {
  const isImage = file.raw.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请上传图片文件')
    return false
  }
  const isLt2M = file.raw.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  coverFile.value = file.raw
  coverPreview.value = URL.createObjectURL(file.raw)
  return false
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    // 如果有新封面，先上传
    if (coverFile.value) {
      const uploadRes = await uploadCover(coverFile.value)
      form.cover_image = uploadRes.url
    }

    if (isEdit.value) {
      await updateBook(form.id, form)
      ElMessage.success('图书更新成功')
    } else {
      await createBook(form)
      ElMessage.success('图书添加成功')
    }
    dialogVisible.value = false
    loadBooks()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除《${row.title}》吗？`, '提示', {
      type: 'warning'
    })
    await deleteBook(row.id)
    ElMessage.success('删除成功')
    loadBooks()
  } catch {
    // 取消
  }
}

function openBorrowDialog(row) {
  borrowForm.bookId = row.id
  borrowForm.bookTitle = row.title
  borrowForm.days = 30
  borrowDialogVisible.value = true
}

async function handleBorrow() {
  borrowLoading.value = true
  try {
    await borrowBook({ book_id: borrowForm.bookId, days: borrowForm.days })
    ElMessage.success('借阅成功')
    borrowDialogVisible.value = false
    loadBooks()
  } finally {
    borrowLoading.value = false
  }
}

onMounted(loadBooks)
</script>

<style scoped lang="scss">
.toolbar-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 16px 20px;
  }
}

.toolbar-form {
  .el-form-item {
    margin-bottom: 0;
    margin-right: 12px;
  }
}

.book-col {
  margin-bottom: 20px;
}

.book-card {
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-4px);
  }

  :deep(.el-card__body) {
    padding: 0;
  }
}

.book-cover-wrapper {
  position: relative;
  width: 100%;
  padding-top: 140%;
  background: #f5f7fa;
  overflow: hidden;
}

.book-cover {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  image-rendering: high-quality;
}

.cover-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  background: #f5f7fa;
}

.placeholder-text {
  margin-top: 8px;
  font-size: 14px;
}

.book-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 1;
}

.book-info {
  padding: 12px;
}

.book-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.book-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.book-stock {
  font-size: 12px;

  &.in-stock {
    color: #67c23a;
  }

  &.out-stock {
    color: #f56c6c;
  }
}

.book-location {
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.book-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 16px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.cover-uploader {
  :deep(.el-upload) {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
    width: 120px;
    height: 168px;
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover {
      border-color: #409eff;
    }
  }
}

.cover-preview {
  width: 120px;
  height: 168px;
  object-fit: cover;
  display: block;
}

.cover-preview-wrapper {
  position: relative;
  width: 120px;
  height: 168px;

  &:hover .cover-overlay {
    opacity: 1;
  }
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 12px;
}

.cover-upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
  font-size: 12px;
  gap: 6px;
}
</style>
