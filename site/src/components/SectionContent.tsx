import type { Section } from "../routes";
import { Example } from "./Example";
import { Command } from "./Command";

export function SectionContent({ section, level = 2 }: { section: Section; level?: 2 | 3 }) {
  const Heading = level === 3 ? "h3" : "h2";
  return (
    <section id={section.id}>
      <Heading>{section.title}</Heading>
      {section.paragraphs.map((p) => <p key={p}>{p}</p>)}
      {section.command && <Command>{section.command}</Command>}
      {section.example && <Example name={section.example} />}
      {section.table && (
        <div className="table-scroll" tabIndex={0} role="region" aria-label={section.title}>
          <table>
            <thead><tr>{section.table.headers.map((header) => <th scope="col" key={header}>{header}</th>)}</tr></thead>
            <tbody>{section.table.rows.map((row) => (
              <tr key={row[0]}>{row.map((cell, index) => index === 0
                ? <th scope="row" key={cell}>{cell}</th>
                : <td key={cell}>{cell}</td>)}</tr>
            ))}</tbody>
          </table>
        </div>
      )}
      {section.links && (
        <ul className="related">{section.links.map(([name, href]) => (
          <li key={href}><a href={href}>{name}</a></li>
        ))}</ul>
      )}
    </section>
  );
}
