import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { addComment } from "@/lib/actions";

export function CommentForm({ postId }: { postId: string }) {
  const action = addComment.bind(null, postId);

  return (
    <form action={action} className="space-y-3 rounded-lg border p-4">
      <div className="grid gap-3 sm:grid-cols-[200px_1fr]">
        <Input name="author" placeholder="닉네임" required maxLength={50} />
        <Textarea
          name="content"
          placeholder="댓글을 입력하세요"
          required
          rows={2}
        />
      </div>
      <div className="flex justify-end">
        <Button type="submit" size="sm">
          댓글 등록
        </Button>
      </div>
    </form>
  );
}
