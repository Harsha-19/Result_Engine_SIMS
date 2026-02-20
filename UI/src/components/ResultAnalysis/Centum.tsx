import React from "react";

interface CentumProps {
  centum: {
    slNo: number;
    name: string;
    usn: string;
    subject: string;
  }[];
}

export const CentumAchievers: React.FC<CentumProps> = ({ centum }) => {
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
                <th className="p-3">Name</th>
                <th className="p-3">Registration No.</th>
                <th className="p-3 rounded-tr-2xl">Subject</th>
              </tr>
            </thead>
            <tbody>
              {centum.map((student) => (
                <tr key={student.slNo} className="border-b">
                  <td className="p-3 text-center">{student.slNo}</td>
                  <td className="p-3 font-medium">{student.name}</td>
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
