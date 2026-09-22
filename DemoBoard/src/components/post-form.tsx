import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export function PostForm({
  action,
  defaultTitle = "",
  defaultAuthor = "",
  defaultContent = "",
  submitLabel = "등록",
}: {
  action: (formData: FormData) => void | Promise<void>;
  defaultTitle?: string;
  defaultAuthor?: string;
  defaultContent?: string;
  submitLabel?: string;
}) {
  return (
    <form action={action} className="space-y-5">
      <div className="space-y-2">
        <Label htmlFor="title">제목</Label>
        <Input
          id="title"
          name="title"
          defaultValue={defaultTitle}
          placeholder="제목을 입력하세요"
          required
          maxLength={200}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="author">작성자</Label>
        <Input
          id="author"
          name="author"
          defaultValue={defaultAuthor}
          placeholder="닉네임을 입력하세요"
          required
          maxLength={50}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="content">내용</Label>
        <Textarea
          id="content"
          name="content"
          defaultValue={defaultContent}
          placeholder="내용을 입력하세요"
          required
          rows={12}
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="submit">{submitLabel}</Button>
      </div>
    </form>
  );
}
