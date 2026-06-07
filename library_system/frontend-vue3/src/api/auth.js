import request from '@/utils/request'

export function login(data) {
  const formData = new URLSearchParams()
  formData.append('username', data.username)
  formData.append('password', data.password)

  return request({
    url: '/auth/login',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

export function getUserInfo() {
  return request({
    url: '/users/me',
    method: 'get'
  })
}
