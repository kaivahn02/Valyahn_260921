"use client";

import { useTransition } from "react";
import { Button } from "@/components/ui/button";
import { deleteComment } from "@/lib/actions";

export function DeleteCommentButton({
  postId,
  commentId,
}: {
  postId: string;
  commentId: string;
}) {
  const [isPending, startTransition] = useTransition();

  return (
    <Button
      type="button"
      variant="ghost"
      size="sm"
      disabled={isPending}
      onClick={() => {
        if (confirm("댓글을 삭제하시겠습니까?")) {
          startTransition(() => deleteComment(postId, commentId));
        }
      }}
    >
      삭제
    </Button>
  );
}
