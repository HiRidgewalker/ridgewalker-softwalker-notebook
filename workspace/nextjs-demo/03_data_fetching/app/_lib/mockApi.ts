// 模拟一个数据源
// 在真实场景里这就是 fetch('https://api.example.com/...')

const counter = { value: 0 }

export async function fetchUsers(opts?: { revalidate?: number; noStore?: boolean }) {
  // 模拟网络延迟
  await new Promise(r => setTimeout(r, 200))
  counter.value += 1
  return {
    requestCount: counter.value,
    timestamp: new Date().toISOString(),
    users: [
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' },
      { id: 3, name: 'Charlie' },
    ],
  }
}

export async function fetchPosts() {
  await new Promise(r => setTimeout(r, 200))
  return {
    posts: [
      { id: 1, title: '第一篇文章' },
      { id: 2, title: '第二篇文章' },
    ],
  }
}
