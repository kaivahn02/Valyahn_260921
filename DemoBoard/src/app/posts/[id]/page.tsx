import Link from "next/link";
import { notFound } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { CommentForm } from "@/components/comment-form";
import { DeleteCommentButton } from "@/components/delete-comment-button";
import { DeletePostButton } from "@/components/delete-post-button";
import { incrementViews } from "@/lib/actions";
import { getComments, getPost } from "@/lib/store";

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString("ko-KR");
}

export default async function PostPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  await incrementViews(id);

  const post = await getPost(id);
  if (!post) {
    notFound();
  }

  const comments = await getComments(id);

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-10">
      <Link href="/" className="text-sm text-muted-foreground hover:underline">
        ← 목록으로
      </Link>

      <div className="mt-4 space-y-3 border-b pb-6">
        <h1 className="text-2xl font-bold">{post.title}</h1>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
          <span>{post.author}</span>
          <span>·</span>
          <span>{formatDateTime(post.createdAt)}</span>
          {post.updatedAt !== post.createdAt ? (
            <Badge variant="secondary">수정됨</Badge>
          ) : null}
          <span className="ml-auto">조회 {post.views}</span>
        </div>
      </div>

      <div className="min-h-40 whitespace-pre-wrap py-6 leading-relaxed">
        {post.content}
      </div>

      <div className="flex justify-end gap-2 pb-8">
        <Button
          variant="outline"
          render={<Link href={`/posts/${post.id}/edit`} />}
          nativeButton={false}
        >
          수정
        </Button>
        <DeletePostButton postId={post.id} />
      </div>

      <Separator className="mb-8" />

      <section className="space-y-4">
        <h2 className="text-lg font-semibold">댓글 {comments.length}개</h2>

        <div className="space-y-3">
          {comments.map((comment) => (
            <div key={comment.id} className="rounded-lg border p-4">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-sm font-medium">{comment.author}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDateTime(comment.createdAt)}
                  </p>
                </div>
                <DeleteCommentButton postId={post.id} commentId={comment.id} />
              </div>
              <p className="mt-2 whitespace-pre-wrap text-sm">
                {comment.content}
              </p>
            </div>
          ))}
          {comments.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              아직 댓글이 없습니다. 첫 댓글을 남겨보세요.
            </p>
          ) : null}
        </div>

        <CommentForm postId={post.id} />
      </section>
    </main>
  );
}
