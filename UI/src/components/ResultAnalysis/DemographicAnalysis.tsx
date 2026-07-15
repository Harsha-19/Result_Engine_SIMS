import React from "react";

interface DemographicAnalysisProps {
  demographics: any;
}

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

  const categories = demographics?.meta?.categories || ["GENERAL", "OBC", "SC", "ST"];
  const genders = demographics?.meta?.genders || ["MALE", "FEMALE"];

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
              {genders.map((gen: string, idx: number) => (
                <th key={gen} className={`p-3 ${idx === genders.length - 1 ? 'rounded-tr-2xl' : ''}`}>
                  {gen.charAt(0).toUpperCase() + gen.slice(1).toLowerCase()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {categories.map((cat: string) => (
              <tr key={cat} className="border-b">
                <td className="p-3 font-medium">{cat}</td>
                {genders.map((gen: string) => (
                  <td key={gen} className="p-3 text-center">
                    {block?.[cat]?.[gen] ?? 0}
                  </td>
                ))}
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
