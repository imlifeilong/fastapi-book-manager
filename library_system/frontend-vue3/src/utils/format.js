import dayjs from 'dayjs'

export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return '--'
  return dayjs(date).format(format)
}

export function formatDateTime(date) {
  if (!date) return '--'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

export function formatMoney(cents) {
  if (!cents) return '¥0.00'
  return '¥' + (cents / 100).toFixed(2)
}

export function getStatusType(status) {
  const map = {
    borrowed: 'primary',
    returned: 'success',
    overdue: 'danger',
    renewed: 'warning'
  }
  return map[status] || 'info'
}

export function getStatusLabel(status) {
  const map = {
    borrowed: '借阅中',
    returned: '已归还',
    overdue: '已逾期',
    renewed: '已续借'
  }
  return map[status] || status
}

export function getRoleLabel(role) {
  const map = {
    admin: '管理员',
    librarian: '图书管理员',
    reader: '读者'
  }
  return map[role] || role
}

export function getRoleType(role) {
  const map = {
    admin: 'danger',
    librarian: 'warning',
    reader: 'success'
  }
  return map[role] || 'info'
}
