"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import * as store from "./store";

function requireString(formData: FormData, field: string): string {
  const value = formData.get(field);
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`${field}은(는) 필수 입력값입니다.`);
  }
  return value.trim();
}

export async function createPost(formData: FormData) {
  const title = requireString(formData, "title");
  const author = requireString(formData, "author");
  const content = requireString(formData, "content");

  const post = await store.createPost({ title, author, content });

  revalidatePath("/");
  redirect(`/posts/${post.id}`);
}

export async function updatePost(postId: string, formData: FormData) {
  const title = requireString(formData, "title");
  const author = requireString(formData, "author");
  const content = requireString(formData, "content");

  await store.updatePost(postId, { title, author, content });

  revalidatePath("/");
  revalidatePath(`/posts/${postId}`);
  redirect(`/posts/${postId}`);
}

export async function deletePost(postId: string) {
  await store.deletePost(postId);

  revalidatePath("/");
  redirect("/");
}

export async function incrementViews(postId: string) {
  await store.incrementViews(postId);
}

export async function addComment(postId: string, formData: FormData) {
  const author = requireString(formData, "author");
  const content = requireString(formData, "content");

  await store.addComment(postId, { author, content });

  revalidatePath(`/posts/${postId}`);
}

export async function deleteComment(postId: string, commentId: string) {
  await store.deleteComment(commentId);

  revalidatePath(`/posts/${postId}`);
}
