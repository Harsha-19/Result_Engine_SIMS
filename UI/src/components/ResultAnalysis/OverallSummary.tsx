import React from "react";

export const OverallSummary = ({ summary }: { summary: any[] }) => {
  return (
    <div className="bg-card p-8 rounded-3xl shadow-lg border border-border/50 space-y-6 transition-colors">
      <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <span className="w-1.5 h-8 bg-gradient-to-b from-primary to-blue-600 rounded-full"></span>
        I. Overall Summary
      </h3>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-gradient-to-r from-primary to-blue-600 text-primary-foreground">
              <th className="p-3 text-left rounded-tl-2xl">Category</th>
              <th className="p-3">Students Appeared</th>
              <th className="p-3">Distinction (85%-100%)</th>
              <th className="p-3">First Class (60%-85%)</th>
              <th className="p-3">Second Class (50%-60%)</th>
              <th className="p-3">Pass Class (40%-50%)</th>
              <th className="p-3">Total Passed</th>
              <th className="p-3">Total Failed</th>
              <th className="p-3 rounded-tr-2xl">Pass %</th>
            </tr>
          </thead>

          <tbody>
            {summary.map((row, idx) => {
              const isTotal = idx === 2;

              return (
                <tr
                  key={idx}
                  className={
                    isTotal
                      ? "font-semibold bg-gradient-to-r from-green-200 to-green-100 dark:from-emerald-900 dark:to-emerald-800 text-black dark:text-white transition-colors"
                      : "hover:bg-muted/30 dark:hover:bg-muted/20 transition-colors"
                  }
                >
                  <td
                    className={
                      isTotal
                        ? "p-3 rounded-bl-2xl border-b-2 border-emerald-500/40"
                        : "p-3 font-medium bg-muted/30 dark:bg-muted/20 border-t border-b border-border/50"
                    }
                  >
                    {row.category}
                  </td>

                  <td className={isTotal ? "p-3 border-b-2 border-emerald-500/40" : "p-3 border-t border-b border-border/50"}>
                    {row.studentsAppeared}
                  </td>

                  <td className={isTotal ? "p-3 border-b-2 border-emerald-500/40" : "p-3 border-t border-b border-border/50"}>
                    {row.distinction}
                  </td>

                  <td className={isTotal ? "p-3 border-b-2 border-emerald-500/40" : "p-3 border-t border-b border-border/50"}>
                    {row.firstClass}
                  </td>

                  <td className={isTotal ? "p-3 border-b-2 border-emerald-500/40" : "p-3 border-t border-b border-border/50"}>
                    {row.secondClass}
                  </td>

                  <td className={isTotal ? "p-3 border-b-2 border-emerald-500/40" : "p-3 border-t border-b border-border/50"}>
                    {row.passClass}
                  </td>

                  <td className={isTotal ? "p-3 border-b-2 border-emerald-500/40" : "p-3 border-t border-b border-border/50"}>
                    {row.totalPassed}
                  </td>

                  <td className={isTotal ? "p-3 border-b-2 border-emerald-500/40" : "p-3 border-t border-b border-border/50"}>
                    {row.totalFailed}
                  </td>

                  <td
                    className={
                      isTotal
                        ? "p-3 rounded-br-2xl border-b-2 border-emerald-500/40"
                        : "p-3 border-t border-b border-border/50"
                    }
                  >
                    {row.passPercentage}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
