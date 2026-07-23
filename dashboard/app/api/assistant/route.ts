import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const userMessage = body.message || 'Hello';
    return NextResponse.json({ reply: `I received your message: "${userMessage}" `});
  } catch (error) {
    return NextResponse.json({ reply: 'I encountered an error but I am here to help!' });
  }
}
