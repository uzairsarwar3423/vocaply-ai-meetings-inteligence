"use client";

import React from "react";
import { CheckCircle2, ArrowRight, Lightbulb } from "lucide-react";

interface DecisionsProps {
    decisions: string[];
    nextSteps?: string[];
}

export const Decisions: React.FC<DecisionsProps> = ({ decisions, nextSteps }) => {
    const hasDecisions = decisions && decisions.length > 0;
    const hasNextSteps = nextSteps && nextSteps.length > 0;

    return (
        <div className="bg-white rounded-3xl border border-neutral-100 p-5 shadow-sm h-full space-y-5">
            {/* Decisions */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-emerald-50 rounded-xl flex items-center justify-center">
                            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        </div>
                        <h4 className="font-bold text-neutral-800 text-sm">Decisions Made</h4>
                    </div>
                    {hasDecisions && (
                        <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                            {decisions.length}
                        </span>
                    )}
                </div>

                {hasDecisions ? (
                    <ul className="space-y-2.5">
                        {decisions.map((d, i) => (
                            <li key={i} className="flex items-start gap-2.5">
                                <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                                <p className="text-sm text-neutral-600 leading-relaxed">{d}</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-xs text-neutral-400 italic">No explicit decisions recorded.</p>
                )}
            </div>

            {/* Next Steps */}
            {hasNextSteps && (
                <div className="pt-4 border-t border-neutral-100">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 bg-violet-50 rounded-xl flex items-center justify-center">
                            <ArrowRight className="w-4 h-4 text-violet-500" />
                        </div>
                        <h4 className="font-bold text-neutral-800 text-sm">Next Steps</h4>
                    </div>
                    <ul className="space-y-2.5">
                        {nextSteps!.map((step, i) => (
                            <li key={i} className="flex items-start gap-2.5">
                                <div className="w-1.5 h-1.5 rounded-full bg-violet-400 flex-shrink-0 mt-2" />
                                <p className="text-sm text-neutral-600 leading-relaxed">{step}</p>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {!hasDecisions && !hasNextSteps && (
                <div className="flex items-center gap-2 text-xs text-neutral-400 pt-2">
                    <Lightbulb className="w-3.5 h-3.5" />
                    Nothing to follow up on
                </div>
            )}
        </div>
    );
};
