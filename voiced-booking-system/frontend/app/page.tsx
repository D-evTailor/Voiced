export default function Page() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-center mb-8">
        Voice Booking System
      </h1>
      <div className="text-center">
        <p className="text-lg text-gray-600 mb-4">
          Frontend implementation coming soon...
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-800">
            Backend API is running at{" "}
            <a 
              href="/api/" 
              className="text-blue-600 hover:underline"
            >
              /api/
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
