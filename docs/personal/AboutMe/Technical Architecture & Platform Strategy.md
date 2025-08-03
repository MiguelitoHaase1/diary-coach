# Technical Architecture & Platform Strategy

Michael is planning to build a digital product that serves as an architecture enabling other products to be built on top of it. The goal is to create a flexible foundation, allowing individual countries (referred to as affiliates in his company) to develop their own software or front-end experiences related to something called [[Noble Connect]], using whatever tech stack is most convenient for them, including low-code or no-code tools like [[Webflow]]. 

Michael wants to make it clear in the memo that different countries (affiliates) have varying needs and budgets. Some might afford expensive setups like a [[Salesforce]] tech stack, while others would prefer using more affordable and iterative low-code or no-code tools like [[Webflow]] due to cost constraints. He is also likely to include [[Headless API]] as a key technology for this architecture. 

Additionally, Michael wants to include a headless API for the CRM that tracks patient interactions, likely built on top of [[Salesforce]]. He also wants to implement a [[Headless CMS]] (Content Management System) that manages assets for front pages, allowing individual countries to add, delete, whitelist, or blacklist assets, and personalize content for users. 

Michael wants to include an API for an algorithm that personalizes the front page based on everything known about an individual patient. The architecture should include playbooks for managing [[MLR]] (Medical, Legal, Regulatory) and [[PRB]] (Pharmaceutical Regulatory Board) processes, as well as a visual identity playbook. 

The goal is to make it easy to plug in APIs and build custom solutions, while offering a preferred stack that's user-friendly but allowing flexibility for other stacks. Michael wants to ensure that the memo clearly communicates to the tech lead that the goal is to build the foundational 'picks and shovels' while being actively involved in the process. 

Additionally, for each front-end tool, there should be a whitelist of approved tools, including no-code and low-code options, along with a playbook for navigating risk assessments and compliance. This will help affiliates quickly choose and implement tools while adhering to corporate security and compliance standards. 

Michael also wants to ensure that the tech lead understands they will be working in a trio alongside a product owner and a lead designer on this project. The design lead will focus on creating a visual identity and guidance for implementing the architecture in different regions, ensuring affiliates have robust support and are not left to work entirely on their own. 

The overarching framing of the memo should emphasize that while regions are encouraged to build their own solutions tailored to their needs, they should do so by 'standing on the shoulders of giants' in terms of architecture, design, and guidance.

Michael wants to ensure that there is a centralized data capture architecture across regions, allowing for the collection of patient behavior data, even with diverse front-end experiences. This centralized data architecture should inform future personalization and experiences, and it falls within the scope for the tech lead to manage.

Michael is working on non-functional requirements in his project, particularly aspects like load time and overall performance, and plans to address these with his colleague [[Cornelius]]. His email about non-functional requirements is intended for the IT team, who are evaluating whether to use XWeb or another stack for the front-end experience of a product. The feature requirements were created by senior stakeholders, including [[Cornelius]], and now the IT team is assessing the importance of non-functional requirements in making the final decision. Michael aims to emphasize these points in a polite and non-demanding manner in his communication, encouraging a sense of freedom and ownership among his team.

## Related
- [[Product Vision & Strategy]]
- [[Digital Health Experience]]
- [[Technical Learning Areas]]