import React from "react";

export interface CentumStudent {
  slNo: number;
  name: string;
  usn: string;
  subject: string;
  nameMissing?: boolean;
}

interface CentumProps {
  centum: CentumStudent[];
  onCentumChange?: (updatedCentum: CentumStudent[]) => void;
}

export const CentumAchievers: React.FC<CentumProps> = ({ centum, onCentumChange }) => {
  const [localNames, setLocalNames] = React.useState<Record<string, string>>({});

  React.useEffect(() => {
    const initial: Record<string, string> = {};
    centum.forEach((student) => {
      // Initialize with existing USN mapping
      if (!initial[student.usn]) {
        initial[student.usn] = student.name || "";
      }
    });
    setLocalNames(initial);
  }, [centum]);

  React.useEffect(() => {
    if (onCentumChange && centum.length > 0) {
      const updatedCentum = centum.map((student) => ({
        ...student,
        name: localNames[student.usn] || student.name || "Name Not Provided",
      }));
      onCentumChange(updatedCentum);
    }
  }, [localNames, centum, onCentumChange]);

  const updateName = (usn: string, value: string) => {
    setLocalNames((prev) => ({
      ...prev,
      [usn]: value,
    }));
  };

  return (
    <div className="bg-card p-8 rounded-3xl shadow-lg border border-border/50 space-y-6">
      <h3 className="text-2xl font-bold flex items-center gap-2">
        <span className="w-1.5 h-8 bg-gradient-to-b from-yellow-500 to-orange-600 rounded-full"></span>
        V. Centum Achievers
      </h3>

      {centum.length === 0 ? (
        <p className="text-muted-foreground">No centum achievers found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-gradient-to-r from-primary to-blue-600 text-white">
                <th className="p-3 rounded-tl-2xl">Sl.No</th>
                <th className="p-3 text-left">Name</th>
                <th className="p-3 text-center">Registration No.</th>
                <th className="p-3 rounded-tr-2xl text-left">Subject</th>
              </tr>
            </thead>
            <tbody>
              {centum.map((student) => (
                <tr key={student.slNo} className="border-b hover:bg-muted/30 transition">
                  <td className="p-3 text-center">{student.slNo}</td>
                  <td className="p-3 font-medium">
                    {student.nameMissing ? (
                      <input
                        type="text"
                        placeholder="Enter Student Name"
                        className="w-full bg-muted rounded-md px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-primary"
                        value={localNames[student.usn] || ""}
                        onChange={(e) => updateName(student.usn, e.target.value)}
                      />
                    ) : (
                      <span>{student.name}</span>
                    )}
                  </td>
                  <td className="p-3 text-center">{student.usn}</td>
                  <td className="p-3">{student.subject}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
