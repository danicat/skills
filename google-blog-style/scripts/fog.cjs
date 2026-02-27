#!/usr/bin/env node

/**
 * Calculates the Gunning Fog Index for a given text file.
 * Formula: 0.4 * ( (words / sentences) + 100 * (complexWords / words) )
 * 
 * Logic adapted from the Speedgrapher Go implementation for consistency.
 */

const fs = require('fs');

if (process.argv.length < 3) {
  console.error("Usage: node fog.js <filename>");
  process.exit(1);
}

const filename = process.argv[2];

try {
  const text = fs.readFileSync(filename, 'utf8');
  
  // Sentence Counting: Matches Speedgrapher's simple punctuation check
  // Note: Speedgrapher uses regexp.MustCompile(`[.!?]+`)
  const sentences = (text.match(/[.!?]+/g) || []).length || 1;

  // Word Counting: Speedgrapher removes punctuation then splits by space.
  // We'll mimic this: remove punctuation, then split on whitespace.
  const cleanText = text.replace(/[!"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]/g, ''); 
  const words = cleanText.split(/\s+/).filter(w => w.length > 0);
  const wordCount = words.length;
  
  if (wordCount === 0) {
    console.log("Gunning Fog Index: 0 (No words found)");
    process.exit(0);
  }

  // Complex Words: 3+ syllables
  // Speedgrapher Syllables: Counts [aeiouy]+ groups. 
  const complexWordCount = words.filter(w => {
    const vowelGroups = w.match(/[aeiouy]+/gi);
    const syllables = vowelGroups ? vowelGroups.length : 1; // Speedgrapher defaults to 1 if no vowels
    return syllables >= 3;
  }).length;

  const avgSentenceLength = wordCount / sentences;
  const percentComplexWords = (complexWordCount / wordCount) * 100;
  
  const fogIndex = 0.4 * (avgSentenceLength + percentComplexWords);
  
  console.log(`Gunning Fog Index: ${fogIndex.toFixed(2)}`);
  
  // Classification aligned with Speedgrapher
  // >= 18: Hard to Read
  // >= 13: Professional
  // >= 9: General
  // < 9: Simplistic
  if (fogIndex >= 18) {
     console.log("Readability: Hard to Read (Try shortening sentences)");
  } else if (fogIndex >= 13) {
     console.log("Readability: Professional Audiences (Acceptable for technical docs)");
  } else if (fogIndex >= 9) {
     console.log("Readability: General Audiences (Ideal)");
  } else {
     console.log("Readability: Simplistic");
  }

} catch (err) {
  console.error(`Error reading file: ${err.message}`);
  process.exit(1);
}