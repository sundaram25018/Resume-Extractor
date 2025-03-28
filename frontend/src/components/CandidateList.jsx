export default function CandidateList({ candidates }) {
  return (
    <div className="mt-6 w-full max-w-2xl">
      {candidates.map((candidate, index) => (
        <div key={index} className="bg-white p-4 rounded-lg shadow-lg mb-2 text-gray-900">
          <h3 className="text-lg font-semibold">{candidate.name}</h3>
          <p>{candidate.email}</p>
          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-xl">
            Match Score: {candidate.match_score}
          </span>
        </div>
      ))}
    </div>
  );
}
