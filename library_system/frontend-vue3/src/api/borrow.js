import request from '@/utils/request'

export function borrowBook(data) {
  return request({
    url: '/borrows/borrow',
    method: 'post',
    data
  })
}

export function returnBook(data) {
  return request({
    url: '/borrows/return',
    method: 'post',
    data
  })
}

export function renewBook(data) {
  return request({
    url: '/borrows/renew',
    method: 'post',
    data
  })
}

export function getMyBorrows(params) {
  return request({
    url: '/borrows/my-borrows',
    method: 'get',
    params
  })
}

export function getAllBorrows(params) {
  return request({
    url: '/borrows/all',
    method: 'get',
    params
  })
}

export function getBorrowStatistics() {
  return request({
    url: '/borrows/statistics',
    method: 'get'
  })
}

export function checkOverdue() {
  return request({
    url: '/borrows/check-overdue',
    method: 'post'
  })
}
