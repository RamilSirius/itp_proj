"""English stop-words and tiny sentiment lexicon.

These are deliberately small, hand-curated lists so the project has zero
external dependencies. They are good enough for demo-quality results on
classic public-domain books.
"""

from __future__ import annotations

from typing import FrozenSet

# A compact set of common English stop words (use ``set`` per the rubric).
STOPWORDS: FrozenSet[str] = frozenset({
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into",
    "is", "it", "its", "itself", "just", "let", "me", "more", "most",
    "must", "my", "myself", "no", "nor", "not", "now", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "said", "same", "say", "shall", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those",
    "through", "thus", "to", "too", "under", "until", "up", "upon", "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who",
    "whom", "why", "will", "with", "would", "you", "your", "yours",
    "yourself", "yourselves",
})

# Lexicon for sentiment analysis. The rubric only asks for a built-in word
# list; the words here are the most reliable signal-bearers in classic prose.
POSITIVE_WORDS: FrozenSet[str] = frozenset({
    "good", "great", "happy", "joy", "joyful", "love", "loved", "lovely",
    "wonderful", "wonder", "beautiful", "beauty", "bright", "kind",
    "kindly", "pleased", "pleasure", "delight", "delighted", "smile",
    "smiled", "laugh", "laughed", "cheerful", "warm", "sweet", "fortunate",
    "lucky", "hope", "hopeful", "peace", "peaceful", "friendly", "friend",
    "win", "won", "success", "successful", "excellent", "amazing",
    "magnificent", "splendid", "fine", "merry", "best", "better",
})

NEGATIVE_WORDS: FrozenSet[str] = frozenset({
    "bad", "terrible", "awful", "horrible", "sad", "angry", "anger", "hate",
    "hated", "fear", "feared", "afraid", "cry", "cried", "wept", "weep",
    "miserable", "misery", "pain", "painful", "hurt", "wound", "wounded",
    "evil", "wicked", "cruel", "cruelly", "dark", "darkness", "death",
    "dead", "dying", "die", "killed", "kill", "lost", "lose", "lonely",
    "alone", "worse", "worst", "tragic", "tragedy", "doom", "doomed",
    "hopeless", "despair", "grief", "broken",
})
