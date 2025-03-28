export default function Button({ onClick, children, className }) {
  return (
    <button onClick={onClick} className={`p-2 rounded-lg text-white ${className}`}>
      {children}
    </button>
  );
}
