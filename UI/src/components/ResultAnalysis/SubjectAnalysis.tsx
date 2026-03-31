import React from "react";

interface Subject {
  id: number;
  slNo: string;
  subject: string;
  section?: string;
  faculty?: string;
  passed: number;
  failed: number;
  absent: number;
  centum: number;
  passPercent: number;
  topper: number;
}

interface SubjectMeta {
  subject: string;
  section: string;
  faculty: string;
}

interface Props {
  subjects: Subject[];
  onMetaChange?: (meta: SubjectMeta[]) => void;
}

export const SubjectAnalysis: React.FC<Props> = ({ subjects, onMetaChange }) => {
  const [localMeta, setLocalMeta] = React.useState<Record<number, { section: string; faculty: string }>>({});

  // Sync when subjects change (e.g. after fresh analysis)
  React.useEffect(() => {
    const initial: Record<number, { section: string; faculty: string }> = {};
    subjects.forEach((sub) => {
      initial[sub.id] = {
        section: sub.section || "",
        faculty: sub.faculty || "",
      };
    });
    setLocalMeta(initial);


    if (onMetaChange) {
      const meta = subjects.map((sub) => ({
        subject: sub.subject,
        section: initial[sub.id]?.section ?? "",
        faculty: initial[sub.id]?.faculty ?? "",
      }));
      onMetaChange(meta);
    }
  }, [subjects, onMetaChange]);

  // Sync to parent whenever localMeta or subjects change
  React.useEffect(() => {
    if (onMetaChange) {
      const meta = subjects.map((sub) => ({
        subject: sub.subject,
        section: localMeta[sub.id]?.section ?? sub.section ?? "",
        faculty: localMeta[sub.id]?.faculty ?? sub.faculty ?? "",
      }));
      onMetaChange(meta);
    }
  }, [localMeta, subjects, onMetaChange]);

  const updateMeta = (id: number, field: "section" | "faculty", value: string) => {
    setLocalMeta((prev) => ({
      ...prev,
      [id]: {
        section: prev[id]?.section ?? "",
        faculty: prev[id]?.faculty ?? "",
        [field]: value,
      },
    }));
  };

  return (
    <div className="bg-card p-8 rounded-3xl shadow-lg border border-border/50">
      <h2 className="text-2xl font-bold mb-6">
        III. Subject-wise Analysis
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gradient-to-r from-primary to-blue-600 text-white text-sm">
              <th className="p-3 text-left">Sl.No</th>
              <th className="p-3 text-left">Subject</th>
              <th className="p-3 text-left">Section</th>
              <th className="p-3 text-left">Faculty Name</th>
              <th className="p-3 text-center">Passed</th>
              <th className="p-3 text-center">Failed</th>
              <th className="p-3 text-center">Absent</th>
              <th className="p-3 text-center">Centum</th>
              <th className="p-3 text-center">Pass %</th>
              <th className="p-3 text-center">Topper %</th>
            </tr>
          </thead>

          <tbody>
            {subjects.map((sub, index) => (
              <tr
                key={index}
                className="border-b hover:bg-muted/30 transition"
              >
                <td className="p-3">{index + 1}</td>
                <td className="p-3 font-medium">{sub.subject}</td>

                {/* Manual Section */}
                <td className="p-3">
                  <input
                    type="text"
                    placeholder="Enter Section"
                    className="w-full bg-muted rounded-md px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-primary"
                    value={localMeta[sub.id]?.section ?? ""}
                    onChange={(e) => updateMeta(sub.id, "section", e.target.value)}
                  />
                </td>

                {/* Manual Faculty */}
                <td className="p-3">
                  <input
                    type="text"
                    placeholder="Enter Faculty Name"
                    className="w-full bg-muted rounded-md px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-primary"
                    value={localMeta[sub.id]?.faculty ?? ""}
                    onChange={(e) => updateMeta(sub.id, "faculty", e.target.value)}
                  />
                </td>

                <td className="p-3 text-center">{sub.passed}</td>
                <td className="p-3 text-center">{sub.failed}</td>
                <td className="p-3 text-center">{sub.absent}</td>
                <td className="p-3 text-center">{sub.centum}</td>
                <td className="p-3 text-center">{sub.passPercent}</td>
                <td className="p-3 text-center">{sub.topper}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
