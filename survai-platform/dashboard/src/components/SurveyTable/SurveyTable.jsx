import React, { useState } from "react";
import {
  Box,
  useMediaQuery,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  Typography,
} from "@mui/material";
import { Add, BarChart } from "@mui/icons-material";
import SearchIcon from "../../assets/Search.svg";
import SearchBar from "../sharedTableComponents/SearchBar";
import MobileTableCard from "./components/MobileTableCard";
import DesktopTable from "./components/DesktopTable";
import TablePagination from "../sharedTableComponents/TablePagination";
import { filterData, paginateData, sortData } from "../../utils/Surveys/surveyTableHelpers";
import { useSurvey } from "../../hooks/Surveys/useSurvey";
import SurveyService from "../../services/Surveys/surveyService";
import SendSurveyDialog from "../Survey/components/SendSurveyDialog";

const DashboardTable = ({
  tableData = [],
  loading: tableLoading = false,
  onRowClick,
  onDataChange,
  onEditSurvey,
  onCloneSurvey,
  emptyStateTitle,
  emptyStateDescription,
  emptyStateButtonLabel,
  onEmptyStateAction,
}) => {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [orderBy, setOrderBy] = useState("LaunchDate");
  const [order, setOrder] = useState("desc");
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [page, setPage] = useState(1);
  
  const [sendDialogOpen, setSendDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedSurvey, setSelectedSurvey] = useState(null);
  const [deletingSurvey, setDeletingSurvey] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [showSuccess, setShowSuccess] = useState(false);
  
  const isMobile = useMediaQuery("(max-width: 600px)");

  const { 
    sendSurveyByEmail, 
    sendSurveyBySMS, 
    isSendingEmail, 
    isSendingSMS 
  } = useSurvey();

  const handleSort = (property) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const handleRowClick = (item) => {
    console.log('Row clicked:', item);
    if (onRowClick) {
      console.log('Calling onRowClick with:', item);
      onRowClick(item);
    } else {
      console.log('No onRowClick function provided');
    }
  };

  const handleSendEmail = (item) => {
    setSelectedSurvey(item);
    setSendDialogOpen(true);
  };

  const handleSendPhone = (item) => {
    setSelectedSurvey(item);
    setSendDialogOpen(true);
  };

  const handleSendDialogClose = () => {
    if (!isSendingEmail && !isSendingSMS) {
      setSendDialogOpen(false);
      setSelectedSurvey(null);
    }
  };

  const handleSendEmailConfirm = async (email, language) => {
    try {
      const emailLang = language || "en";
      const result = await sendSurveyByEmail(
        selectedSurvey.SurveyId, 
        email, 
        emailLang
      );
      
      console.log('Email send result:', result); // Debug log
      
      // Show success message if no error was thrown
      setSuccessMessage(`Survey "${selectedSurvey.Name}" sent successfully to ${email}`);
      setShowSuccess(true);
    } catch (error) {
      console.error('Error sending email:', error);
      const detail = error?.response?.data?.detail || error?.message || "Failed to send email";
      setSuccessMessage(`Error: ${detail}`);
      setShowSuccess(true);
    } finally {
      setSendDialogOpen(false);
      setSelectedSurvey(null);
    }
  };

  const handleSendPhoneConfirm = async (phone, provider = "livekit", language = "en") => {
    try {
      const result = await sendSurveyBySMS(
        selectedSurvey.SurveyId, 
        phone, 
        provider,
        language
      );
      
      console.log('SMS send result:', result);
      
      setSuccessMessage(`Call initiated for "${selectedSurvey.Name}" to ${phone}`);
      setShowSuccess(true);
    } catch (error) {
      console.error('Error sending call:', error);
      const detail = error?.response?.data?.detail || error?.message || "Failed to initiate call";
      setSuccessMessage(`Error: ${detail}`);
      setShowSuccess(true);
    } finally {
      setSendDialogOpen(false);
      setSelectedSurvey(null);
    }
  };

  const handleDeleteSurvey = (item) => {
    setDeletingSurvey(item);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingSurvey) return;
    setIsDeleting(true);
    try {
      await SurveyService.deleteSurvey(deletingSurvey.SurveyId);
      setSuccessMessage(`Survey "${deletingSurvey.Name}" deleted successfully`);
      setShowSuccess(true);
      if (onDataChange) onDataChange();
    } catch (error) {
      setSuccessMessage(`Failed to delete survey: ${error.message}`);
      setShowSuccess(true);
    } finally {
      setIsDeleting(false);
      setDeleteDialogOpen(false);
      setDeletingSurvey(null);
    }
  };

  const handleSuccessClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setShowSuccess(false);
  };

  // Data processing
  let filteredData = filterData(tableData, search);
  if (statusFilter === "active") {
    filteredData = filteredData.filter((item) => item.Status !== "Completed");
  } else if (statusFilter === "completed") {
    filteredData = filteredData.filter((item) => item.Status === "Completed");
  }
  const sortedData = sortData(filteredData, orderBy, order);
  const paginatedData = paginateData(sortedData, page, rowsPerPage);

  const showEmptyState = emptyStateTitle && !tableLoading && tableData.length === 0;
  const useRiderVoiceSearch = Boolean(emptyStateTitle);

  return (
    <Box
      sx={{
        backgroundColor: "#fff",
        p: isMobile ? 2 : 4,
        borderRadius: "20px",
      }}
    >
      {useRiderVoiceSearch ? (
        <Box
          sx={{
            display: "flex",
            flexDirection: isMobile ? "column" : "row",
            gap: 2,
            alignItems: isMobile ? "stretch" : "center",
            mb: 2,
          }}
        >
          <TextField
            size="small"
            placeholder="Search surveys..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <img src={SearchIcon} alt="Search" style={{ width: 18, height: 18 }} />
                </InputAdornment>
              ),
            }}
            sx={{
              flex: 1,
              maxWidth: useRiderVoiceSearch && !isMobile ? 320 : "none",
              "& .MuiOutlinedInput-root": {
                borderRadius: "12px",
                height: "40px",
                backgroundColor: "#fff",
                fontSize: "14px",
                border: "1px solid #E0E0E0",
                "& fieldset": { border: "none" },
              },
            }}
          />
          <FormControl size="small" sx={{ minWidth: isMobile ? "100%" : 160 }}>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              displayEmpty
              sx={{
                borderRadius: "12px",
                height: "40px",
                fontSize: "14px",
                fontFamily: "Poppins, sans-serif",
              }}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
            </Select>
          </FormControl>
        </Box>
      ) : (
        <SearchBar
          title="Active Surveys"
          searchValue={search}
          onSearchChange={setSearch}
          placeholder="Search survey"
        />
      )}

      {showEmptyState ? (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            py: 8,
            px: 2,
          }}
        >
          <BarChart
            sx={{
              fontSize: 80,
              color: "#7B61FF",
              mb: 2,
              opacity: 0.9,
            }}
          />
          <Typography
            sx={{
              fontFamily: "Poppins, sans-serif",
              fontWeight: 600,
              fontSize: "22px",
              color: "#1E1E1E",
              mb: 1,
              textAlign: "center",
            }}
          >
            {emptyStateTitle}
          </Typography>
          <Typography
            sx={{
              fontFamily: "Poppins, sans-serif",
              fontWeight: 400,
              fontSize: "14px",
              color: "#7D7D7D",
              mb: 3,
              textAlign: "center",
              maxWidth: 360,
            }}
          >
            {emptyStateDescription}
          </Typography>
          {onEmptyStateAction && (
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={onEmptyStateAction}
              sx={{
                backgroundColor: "#7B61FF",
                color: "white",
                textTransform: "none",
                borderRadius: "12px",
                fontFamily: "Poppins, sans-serif",
                fontSize: "15px",
                fontWeight: 500,
                px: 3,
                py: 1.5,
                "&:hover": { backgroundColor: "#6A52E0" },
              }}
            >
              {emptyStateButtonLabel || "Create Survey"}
            </Button>
          )}
        </Box>
      ) : (
        <>
          {isMobile ? (
            <Box>
              {paginatedData.map((item) => (
                <MobileTableCard
                  key={item.SurveyId}
                  item={item}
                  onItemClick={handleRowClick}
                  onSendEmail={handleSendEmail}
                  onSendPhone={handleSendPhone}
                />
              ))}
            </Box>
          ) : (
            <DesktopTable
              data={paginatedData}
              onItemClick={handleRowClick}
              orderBy={orderBy}
              order={order}
              onSort={handleSort}
              onSendEmail={handleSendEmail}
              onSendPhone={handleSendPhone}
              onDeleteSurvey={handleDeleteSurvey}
              onEditSurvey={onEditSurvey}
              onCloneSurvey={onCloneSurvey}
            />
          )}

          <TablePagination
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={setRowsPerPage}
            page={page}
            onPageChange={setPage}
            totalItems={sortedData.length}
          />
        </>
      )}

      {/* Send Survey Dialog */}
      <SendSurveyDialog
        open={sendDialogOpen}
        onClose={handleSendDialogClose}
        onConfirmEmail={handleSendEmailConfirm}
        onConfirmPhone={handleSendPhoneConfirm}
        surveyId={selectedSurvey?.SurveyId}
        surveyName={selectedSurvey?.Name}
        isSendingEmail={isSendingEmail}
        isSendingPhone={isSendingSMS}
        surveyStatus={selectedSurvey?.Status}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => !isDeleting && setDeleteDialogOpen(false)}
      >
        <DialogTitle sx={{ fontFamily: 'Poppins, sans-serif', fontWeight: 600 }}>
          Delete Survey
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ fontFamily: 'Poppins, sans-serif' }}>
            Are you sure you want to delete survey "{deletingSurvey?.Name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            onClick={() => setDeleteDialogOpen(false)}
            disabled={isDeleting}
            sx={{ fontFamily: 'Poppins, sans-serif', textTransform: 'none', color: '#666' }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            disabled={isDeleting}
            variant="contained"
            sx={{
              fontFamily: 'Poppins, sans-serif',
              textTransform: 'none',
              backgroundColor: '#D32F2F',
              '&:hover': { backgroundColor: '#B71C1C' },
            }}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Message Snackbar */}
      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={handleSuccessClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleSuccessClose}
          severity={successMessage.startsWith("Error:") ? "error" : "success"}
          variant="filled"
          sx={{
            width: '100%',
            background: successMessage.startsWith("Error:") ? "#FDEDED" : "#EFEFFD",
            color: successMessage.startsWith("Error:") ? "#D32F2F" : "#1958F7",
          }}
        >
          {successMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DashboardTable;