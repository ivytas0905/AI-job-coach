"use client";

import { useState } from "react";

interface Problem { questionId: string; title: string; titleSlug: string; difficulty: string }

export default function LeetCodePage() {
  const [difficulty, setDifficulty] = useState("Medium");
  const [count, setCount] = useState(2);
  const [problems, setProblems] = useState<Problem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function generate() {
    setLoading(true); setError("");
    try { const response = await fetch("/api/leetcode", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ difficulty, count }) }); const data = await response.json(); if (!response.ok) throw new Error(); setProblems(data); }
    catch { setError("暂时无法获取题目，请稍后重试。"); }
    finally { setLoading(false); }
  }
  return <main className="leetcode-page"><section><span className="eyebrow">技术面试准备</span><h1>每日编程练习</h1><p>选择难度和题目数量，生成今天的 LeetCode 练习清单。</p><div className="leetcode-controls"><label>难度<select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>{["Easy","Medium","Hard"].map((value) => <option key={value}>{value}</option>)}</select></label><label>题目数量<select value={count} onChange={(event) => setCount(Number(event.target.value))}>{[1,2,3,5].map((value) => <option key={value}>{value}</option>)}</select></label><button className="button button-primary" disabled={loading} onClick={() => void generate()}>{loading ? "正在生成…" : "生成练习"}</button></div>{error && <p role="alert" className="inline-error">{error}</p>}<ol className="problem-list">{problems.map((problem) => <li key={problem.questionId}><div><strong>{problem.title}</strong><span>{problem.difficulty}</span></div><a href={`https://leetcode.com/problems/${problem.titleSlug}/`} target="_blank" rel="noreferrer">开始解题</a></li>)}</ol></section></main>;
}
