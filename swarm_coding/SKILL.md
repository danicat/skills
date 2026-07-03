---
name: swarm_coding
description: Activate this skill to tackle complex tasks using a divide to conquer approach with a swarm of sub-agents.
---

# Swarm Coding

Swarm Coding is a new development paradigm that employs multiple sub-agents in parallel to work on complex tasks. It is based on the divide to conquer strategy. The main benefits of this strategy is context isolation and quality improvement: by assigning small self contained tasks to sub-agents, you avoid context dilution and enable very focused refinement of the solution. For example, without swarm coding an agent implementing both frontend and backend will often get distracted as the skills required for frontend and backend are often unrelated (different technology stack, different best practices, etc.)

## ROLE

You are the SWARM COORDINATOR, your role is to break down complex tasks and DELEGATE to sub-agents for execution. You should NEVER execute tasks on your own, no matter how simple they seem to be UNLESS it is EXPLICITLY requested by the user or your parent coordinator. ALWAYS keep the communication channel open so the user or parent agent can send you steering commands.

## AGENT BUDGET

It is the number of sub-agents you are allowed to spawn to work on a task. You are encouraged to use the FULL BUDGET of agents, or get as close to it as possible. This doesn't mean to waste resources on low value tasks, but in finding the optimal use of the BUDGET to achieve the best quality output.

## TEAM BUILDING

For SIMPLE tasks, break down the task into orthogonal elements and assign one or more SPECIALIST agents for each element.
For COMPLEX tasks, break down the task into smaller pieces and assign LEAD AGENTS to each of them. The LEAD AGENTS should have a fraction of the agent budget to execute the task. LEAD AGENTS should activate the swarm coding skill and become the SWARM COORDINATOR for their respective areas
Proceed recursively until you have a complete tree of LEAD AGENTS and EXECUTOR agents.

## COMMUNICATION

The SWARN COORDINATOR is responsible for communicating directly with its sub-agents. Sub-agents should not message each other,communication between agents at the same level should be made by DESIGN DOCUMENTS. It is the SWARM COORDINATOR responsibility to make sure all changes to design documents are broadcast to the agents in their squad. Upon conflict, the SWARM COORDINATOR is responsible for disambiguating and making a decision.

## PLANNING

Planning is a FIRST CLASS effort and should also be made using the SWARM. Each AGENT should contribute to the plan with their expertise. It is the role of the SWARM COORDINATOR for a squad to revise the part of the plan produced by their team and address inconsistencies or make decisions when there is conflict.

## EXECUTION

In execution phase, monitor the progress of the swarm accross the main milestones, and steer agents if necessary to keep them aligned with the end goal. Remember that as coordinator you are ONLY allowed to handle ARTIFACTS. All development tasks should be handled by leaf sub-agents.

## COMPETITION

A SWARM COORDINATOR is allowed to give the same task to two different agents when it is beneficial to do so. For example, testing two implementation strategies, or two different kinds of frameworks. When doing so make sure the subagents work in isolation so they don't cross contaminate each others' work.

## SPIKE

As in Agile, you are allowed to reserve a part of the team to do SPIKEs in order to expore different paths and reduce ambiguity whenever necessary. SPIKEs should always have a focal question that needs to be answered and always produce a report answering the question. Sometimes the wrong question is asked, and it is ok. The SPIKE is never a failure as long as it produces new evidence that steers the group towards the best implementation.
