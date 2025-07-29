## Philosophy: Don't overload the agents!

I believe good practices from software development still stand with GenAI... they can just get 10-100X faster with 10X smaller teams. 

Examples of good practices we protect: TDD, Test and deploy frequently, thoughtful emerging architecture designed for anti-fragility, split up learn Vs execute, code reviews, linting...). Most of these practices are covered in the claude.md file I use when coding... but this document will describe the high-level setup. 

The highest level principle behind all this is: **Avoid overloading the AI**: In we do aims to reduce cognitive load, by compartmentalizing tasks.

##Workflow

1 - Upload my **claude.md** file, to have key guidance and context there

2 - Write a **productvision.md** with objectives and JTBDs plus a quick prototype, to ensure high-level business context is available. Define Evals already here

3 - Define a composable architecture... here always consider at least two very distinct approaches before settling on one. The end choice needs to be composable, anti-fragile, and hyper-testable in something close to REPLs. (e.g., CLI front-end)

4 - Based on architecture, decide on a product topology and build appropriate **sub-agents** with particular expertises in their own markdown files to drive each increment (e.g., UI agent, refactoring agent, mcp agent, Evals agent...)... this is like local claude.md files.

5 - Build **roadmap.md**, considering the topology and which things can be run in parallel.

5 - Once start any session, start creating a more detailed **session_x.md** to describe approach and break-into increments

6 - At every session - test and look at Evals - are they improving?

8 - At every increment, create **logbook_x.md** for traceability and an overarching **status.md** --- and push to git

9 - Have an agent read and accept/comment on **pull-requests**

10 - Send all logs and comments in pull requests to claude or gpt to learn from them

11 - Update overarching documents above (product vision, claude.md, individual agent markdowns,...) based on learnings, so we don't repeat mistakes 
