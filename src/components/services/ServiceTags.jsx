export default function ServiceTags({ tags }) {
  return (
    <div className="service-tags">
      {tags.map((tag) => (
        <span key={tag}>{tag}</span>
      ))}
    </div>
  );
}
