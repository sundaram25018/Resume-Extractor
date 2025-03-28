export default function FileUpload({ onFileSelect }) {
  return (
    <div>
      <input 
        type="file" 
        onChange={(e) => onFileSelect(e.target.files[0])} 
        className="mb-4 w-full" 
      />
    </div>
  );
}
