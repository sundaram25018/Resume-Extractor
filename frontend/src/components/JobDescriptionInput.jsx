export default function JobDescriptionInput({ value, onChange }) {
  return (
    <input
      type="text"
      placeholder="Enter Job Description"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="mb-4 w-full p-2 border rounded"
    />
  );
}
