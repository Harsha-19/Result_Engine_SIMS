import React from "react";

interface Props {
  topPerformers: any[];
}

export const TopPerformers: React.FC<Props> = ({ topPerformers }) => {
  console.log(JSON.stringify(topPerformers, null, 2));


  return (
    <div className="bg-card p-8 rounded-3xl shadow-lg border border-border/50">
      <h2 className="text-2xl font-bold mb-6">
        II. Top Performers
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-green-600 text-white text-sm">
              <th className="p-3 text-left">Rank</th>
              <th className="p-3 text-left">Name</th>
              <th className="p-3 text-left">Registration No.</th>
              <th className="p-3 text-left">Marks Obtained</th>
              <th className="p-3 text-left">Percentage</th>
            </tr>
          </thead>

          <tbody>
            {topPerformers.map((student, index) => (
              <tr
                key={index}
                className="border-b hover:bg-muted/30 transition"
              >
                {/* Simple 1, 2, 3 */}
                <td className="p-3 font-bold">{index + 1}</td>

                <td className="p-3">
                  {student.name}
                </td>

                {/* Support both usn & registrationNo */}
                <td className="p-3">
                  {student.registrationNo || student.usn || "-"}
                </td>

                {/* Support both marks & marksObtained */}
                <td className="p-3">
                  {student.marksObtained || student.marks || "-"}
                </td>

                <td className="p-3">
                  {student.percentage}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
