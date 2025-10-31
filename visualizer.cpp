#include <mgl2/mgl.h>
#include <mgl2/fltk.h>
#include <fstream>
#include <vector>
#include <string>
#include <iostream>
using namespace std;

// ------------------- Draw Callback -------------------
int draw_graph(HMGL gr_handle, void *param)
{
    vector<pair<double, double>> *data = (vector<pair<double, double>> *)param;
    mglGraph gr(gr_handle); // Convert HMGL to mglGraph

    mglData X(data->size()), Y(data->size());
    for (size_t i = 0; i < data->size(); i++)
    {
        X.a[i] = (*data)[i].first;
        Y.a[i] = (*data)[i].second;
    }

    // --- Read encoding type from file ---
    std::ifstream encFile("encoding_type.txt");
    std::string encodingType = "Unknown";
    if (encFile.is_open()) {
        std::getline(encFile, encodingType);
        encFile.close();
    }

    // // --- Dynamic title with encoding type ---
    // std::string fullTitle = "Digital Signal Encoding Visualization — " + encodingType;
    // gr.SetFontSize(0.1);  // ↓ smaller title size
    // gr.Title(fullTitle.c_str(), "", 0);  // center-aligned

    // --- Dynamic title with encoding type ---
    std::string fullTitle = "Digital Signal Encoding Visualization — " + encodingType;

    gr.SetRanges(X.Minimal(), X.Maximal(), -2, 2);
    gr.SetFrame(0); 

    gr.SetFontSize(1.2);               // medium title size
    gr.Title(fullTitle.c_str());       // display title properly
    // gr.SetOrigin(0, -0.1);             // push plot slightly down so title is visible

    gr.SetRanges(X.Minimal(), X.Maximal(), -2, 2);
    gr.Axis();
    gr.Grid("xy");
    gr.Label('x', "Time", 0);
    gr.Label('y', "Amplitude", 0);
    gr.Plot(X, Y, "b2");
    return 0;
}

// ------------------- Main Function -------------------
int main()
{
    ifstream file("signal.txt");
    if (!file.is_open())
    {
        cerr << "❌ Error: could not open signal.txt\n";
        return 1;
    }

    vector<pair<double, double>> data;
    double t, y;
    while (file >> t >> y)
        data.push_back({t, y});

    if (data.empty())
    {
        cerr << "⚠️ Error: signal.txt is empty or invalid\n";
        return 1;
    }

    // ✅ Correct signature for MathGL 8.0.1
    mglFLTK *window = new mglFLTK(draw_graph, "Digital Signal Encoding Visualization", &data);
    window->SetSize(1000, 700);
    window->Run();
    delete window;

    return 0;
}

