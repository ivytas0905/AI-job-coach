/* eslint-disable @typescript-eslint/no-explicit-any */
export async function POST(request: Request) {
  const { difficulty, count } = await request.json();
  
  const query = `
  query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
    problemsetQuestionList(
      categorySlug: $categorySlug
      limit: $limit
      skip: $skip
      filters: $filters
    ) {
      total: totalNum
      questions: data {
        acRate
        difficulty
        freqBar
        frontendQuestionId: questionFrontendId
        isFavor
        paidOnly: isPaidOnly
        status
        title
        titleSlug
        topicTags {
          name
          id
          slug
        }
        hasSolution
        hasVideoSolution
      }
    }
  }
`;

const variables = {
  categorySlug: "",
  limit: 50,
  skip: 0,
  filters: {
    difficulty: difficulty.toUpperCase()
  }
};
  
  try {
    const response = await fetch('https://leetcode.com/graphql/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'JobCoach/1.0'
      },
      body: JSON.stringify({ query, variables })
    });
    
    const data = await response.json();
    const problems = data.data.problemsetQuestionList.questions;

    const shuffled = problems.map((p: any) => ({
  questionId: p.frontendQuestionId,
  title: p.title, 
  titleSlug: p.titleSlug,
  difficulty: p.difficulty
})).sort(() => 0.5 - Math.random());
    
    // 随机选择题目
    const selected = shuffled.slice(0, count);
    
    return Response.json(selected);
  } catch  {
    return Response.json({ error: 'Failed to fetch problems' }, { status: 500 });
  }
}