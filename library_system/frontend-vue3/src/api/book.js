import request from '@/utils/request'

export function getBooks(params) {
  return request({
    url: '/books',
    method: 'get',
    params
  })
}

export function searchBooks(params) {
  return request({
    url: '/books/search',
    method: 'get',
    params
  })
}

export function getBookDetail(id) {
  return request({
    url: `/books/${id}`,
    method: 'get'
  })
}

export function createBook(data) {
  return request({
    url: '/books',
    method: 'post',
    data
  })
}

export function updateBook(id, data) {
  return request({
    url: `/books/${id}`,
    method: 'put',
    data
  })
}

export function deleteBook(id) {
  return request({
    url: `/books/${id}`,
    method: 'delete'
  })
}

export function uploadCover(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/books/upload-cover',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
