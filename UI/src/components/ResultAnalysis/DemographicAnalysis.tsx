import React from "react";

interface DemographicAnalysisProps {
  demographics: any;
}

const categories = ["GENERAL", "OBC", "SC", "ST"];
const genders = ["MALE", "FEMALE"];

export const DemographicAnalysis: React.FC<DemographicAnalysisProps> = ({ demographics }) => {
  if (!demographics) {
    return (
      <div className="bg-card p-8 rounded-3xl shadow-lg border">
        <h3 className="text-2xl font-bold">
          IV. Performance Analysis by Demographics
        </h3>
        <p className="text-muted-foreground mt-4">
          No demographic data available.
        </p>
      </div>
    );
  }

  const renderBlock = (title: string, block: any) => (
    <div className="space-y-4">
      <h4 className="text-lg font-semibold text-muted-foreground">
        {title}
      </h4>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-gradient-to-r from-primary to-blue-600 text-white">
              <th className="p-3 rounded-tl-2xl">Category</th>
              <th className="p-3">Male</th>
              <th className="p-3 rounded-tr-2xl">Female</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((cat) => (
              <tr key={cat} className="border-b">
                <td className="p-3 font-medium">{cat}</td>
                <td className="p-3 text-center">
                  {block?.[cat]?.["MALE"] ?? 0}
                </td>
                <td className="p-3 text-center">
                  {block?.[cat]?.["FEMALE"] ?? 0}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div className="bg-card p-8 rounded-3xl shadow-lg border space-y-8">
      <h3 className="text-2xl font-bold flex items-center gap-2">
        <span className="w-1.5 h-8 bg-gradient-to-b from-accent to-green-600 rounded-full"></span>
        IV. Performance Analysis by Demographics
      </h3>

      {renderBlock("Total Number of Students Appeared", demographics.appeared)}
      {renderBlock("Total Number of Students Passed", demographics.passed)}
      {renderBlock(
        "Students Passed with 60% or Above",
        demographics.passed_60
      )}
    </div>
  );
};
