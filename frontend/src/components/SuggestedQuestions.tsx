const ROW_1 = [
  'I want to study abroad, what should I do?',
  'Who is eligible to go on exchange?',
  'What is Waterloo Passport?',
  'When is the application deadline?',
]

const ROW_2 = [
  'How does course credit transfer work?',
  'How competitive is the exchange application?',
  'How long can an exchange last?',
  'How much does an exchange semester cost?',
]

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void
}

interface QuestionRowProps {
  questions: string[]
  direction: 'left' | 'right'
  onSelect: (question: string) => void
}

/**
 * One horizontally-scrolling row of suggested-question pills.
 *
 * Renders the question list twice back to back to create a seamless
 * marquee loop; the second copy is hidden from assistive tech and keyboard
 * navigation since it is a visual duplicate of the first.
 *
 * @param props.questions - Questions to display in this row.
 * @param props.direction - Which way the row drifts.
 * @param props.onSelect - Called with a question's text when its pill is clicked.
 */
function QuestionRow({ questions, direction, onSelect }: QuestionRowProps) {
  return (
    <div className="suggested-questions__row">
      <div className={`suggested-questions__track suggested-questions__track--${direction}`}>
        {[...questions, ...questions].map((question, idx) => {
          const isDuplicate = idx >= questions.length
          return (
            <button
              key={idx}
              type="button"
              className="suggested-questions__pill"
              onClick={() => onSelect(question)}
              aria-hidden={isDuplicate || undefined}
              tabIndex={isDuplicate ? -1 : 0}
            >
              {question}
            </button>
          )
        })}
      </div>
    </div>
  )
}

/**
 * Two rows of example questions drifting slowly in opposite directions
 * beneath the landing hero title, giving new users a zero-effort way to
 * start a conversation.
 *
 * @param props.onSelect - Called with a question's text when a pill is clicked.
 */
export function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="suggested-questions">
      <QuestionRow questions={ROW_1} direction="left" onSelect={onSelect} />
      <QuestionRow questions={ROW_2} direction="right" onSelect={onSelect} />
    </div>
  )
}
