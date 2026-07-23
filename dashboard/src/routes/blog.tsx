import { createFileRoute } from '@tanstack/react-router'
import { getSortedPostsData } from '../../lib/posts'
export const Route = createFileRoute('/blog')({ component: BlogPage, loader: () => getSortedPostsData() })
function BlogPage() {
  const posts = Route.useLoaderData()
  return <div>Blog: {posts.map(p => <p key={p.id}>{p.title}</p>)}</div>
}