// Minimal wxWidgets test app
// Purpose: Verify the filtered wxWidgets snapshot is buildable

#include <wx/wx.h>

class TestFrame : public wxFrame
{
public:
    TestFrame() : wxFrame(nullptr, wxID_ANY, "kwxFetch Test")
    {
        auto *panel = new wxPanel(this);
        auto *sizer = new wxBoxSizer(wxVERTICAL);

        auto *button = new wxButton(panel, wxID_ANY, "Click Me");
        sizer->Add(button, 0, wxALL | wxCENTER, 20);

        button->Bind(wxEVT_BUTTON, [this](wxCommandEvent &)
                     {
            wxMessageBox("kwxFetch build verification successful!", "Test",
                         wxOK | wxICON_INFORMATION, this);
            Close(); });

        panel->SetSizer(sizer);
        SetClientSize(300, 200);
        Centre();
    }
};

class TestApp : public wxApp
{
public:
    bool OnInit() override
    {
        if (!wxApp::OnInit())
            return false;

        auto *frame = new TestFrame();
        frame->Show();
        return true;
    }
};

wxIMPLEMENT_APP(TestApp);
