export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
            {/* Left Side: Illustration or Branding */}
            <div className="hidden md:flex flex-1 bg-primary items-center justify-center p-12 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-full opacity-10">
                    <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-white rounded-full blur-3xl animate-pulse" />
                    <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-secondary rounded-full blur-3xl" />
                </div>

                <div className="relative z-10 max-w-lg text-white">
                    <div className="flex items-center gap-3 mb-10">
                        <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center text-primary font-bold text-2xl">V</div>
                        <span className="text-3xl font-outfit font-bold tracking-tight">Vocaply</span>
                    </div>

                    <h1 className="text-4xl lg:text-5xl font-outfit font-bold mb-6 leading-tight">
                        Turn Meeting Talk <br />
                        <span className="text-secondary">Into Real Action.</span>
                    </h1>

                    <p className="text-lg text-primary-100 font-inter mb-8 leading-relaxed">
                        Join thousands of teams using AI to automate meeting notes, identify commitments, and track progress effortlessly.
                    </p>

                    <div className="space-y-4">
                        {[
                            "Automated AI Transcription",
                            "Action Item Identification",
                            "Multi-platform Integrations",
                            "Team Progress Tracking"
                        ].map((feature) => (
                            <div key={feature} className="flex items-center gap-3">
                                <div className="w-5 h-5 rounded-full bg-secondary flex items-center justify-center">
                                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor font-bold">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                    </svg>
                                </div>
                                <span className="font-inter font-medium text-white/90">{feature}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Right Side: Auth Forms */}
            <div className="flex-1 flex items-center justify-center p-6 md:p-12">
                <div className="w-full max-w-md">
                    <div className="md:hidden flex items-center gap-2 mb-8 justify-center">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold text-xl">V</div>
                        <span className="text-2xl font-outfit font-bold tracking-tight text-gray-900">Vocaply</span>
                    </div>
                    {children}
                </div>
            </div>
        </div>
    );
}
