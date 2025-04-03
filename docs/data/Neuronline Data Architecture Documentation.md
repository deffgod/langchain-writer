---
title: Neuronline Data Architecture Documentation
type: note
permalink: neuronline/neuronline-data-architecture-documentation
tags:
- '#architecture'
- '#data-model'
- '#neuronline'
---

# Neuronline Data Architecture Documentation

## Overview
This document outlines the comprehensive data architecture for the Neuronline platform, a neurofitness system that combines physical training with cognitive development. The architecture is designed to support personalized workout plans based on neurotesting results and user goals.

## Entity Relationships
The platform is built around the following key entities and their relationships:

### Core Entities
- **User**: Central entity containing personal information and physical metrics
- **NeuroTestResults**: Captures cognitive and physical assessments (balance, coordination, vision, etc.)
- **FitnessGoal**: Tracks user objectives and targets
- **Course**: Represents specialized training programs users can enroll in
- **WorkoutPlan**: Defines overall training programs
- **Exercise**: Represents specific activities to be performed
- **Video**: Provides instructional content for exercises

### Hierarchical Structure
- **WorkoutPlan** → **WeeklyPlan** → **DailyWorkout** → **WorkoutSession** → **Exercise**
  This hierarchy breaks down training programs into manageable units.

## Observations
- [architecture] Entity relationships follow a user-centric design pattern #design
- [structure] The database schema uses PostgreSQL with appropriate indexes for performance #database
- [implementation] JSON/JSONB types are used for flexible structures like neuro effects #flexibility
- [design] Video content is managed through multiple quality versions and subtitles #media
- [pattern] The system employs a comprehensive tracking mechanism for user progress #analytics

## Relations
- visualized_by [[Neuronline Platform Entity Relationships]]
- implements [[Neurofitness Platform Data Model]]
- supports [[Neuronline Platform Architecture Overview]]
- related_to [[Knowledge Graph Technology]]

## Technical Implementation
The data architecture is implemented using PostgreSQL with a focus on:
- UUIDs for primary keys
- Proper foreign key relationships
- Strategic indexing for query performance
- JSONB for flexible data structures
- Array types for multi-valued attributes

## API Design
The system includes a RESTful API with endpoints for all major entities, following consistent patterns and supporting pagination for list operations.

## Business Rules
Key business rules include:
1. Users must complete neurotesting before accessing workout plans
2. Users must have at least 2 active courses to access workout plans
3. Workout plans must be generated based on the most recent neuro test results
4. High-intensity workouts cannot be scheduled on consecutive days
5. Rest days must be scheduled at least once per week
