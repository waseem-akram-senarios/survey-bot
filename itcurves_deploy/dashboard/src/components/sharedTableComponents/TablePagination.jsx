import { Box, Typography, Select, MenuItem, Pagination, useMediaQuery, useTheme } from "@mui/material";

const TablePagination = ({ 
  totalItems, 
  rowsPerPage, 
  page, 
  onRowsPerPageChange, 
  onPageChange 
}) => {
  const totalPages = Math.ceil(totalItems / rowsPerPage);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        mt: 2,
        flexWrap: "nowrap",
        gap: 2,
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", fontSize: "14px" }}>
        <Typography
          sx={{
            fontFamily: "Poppins, sans-serif",
            fontWeight: 400,
            fontSize: "14px",
            lineHeight: "18px",
            color: "#9A9EA5",
            mr: 0.5,
          }}
        >
          Rows per page
        </Typography>
        <Select
          size="small"
          value={rowsPerPage}
          onChange={(e) => onRowsPerPageChange(parseInt(e.target.value))}
          sx={{
            height: "28px",
            fontSize: "14px",
            minWidth: "48px",
            mt: 0.5,
            ml: 0.5,
            backgroundColor: "transparent",
            border: "none",
            boxShadow: "none",
            "& .MuiOutlinedInput-notchedOutline": {
              border: "none",
            },
            "& .MuiSelect-select": {
              paddingRight: "24px",
              paddingLeft: "8px",
              fontFamily: "Roboto",
              fontWeight: 500,
              fontSize: "14px",
              lineHeight: "18px",
              color: "#242731",
            },
            "& .MuiSvgIcon-root": {
              color: "#242731",
            },
          }}
          displayEmpty
          renderValue={() => rowsPerPage.toString().padStart(2, "0")}
        >
          <MenuItem value={5}>05</MenuItem>
          <MenuItem value={10}>10</MenuItem>
          <MenuItem value={20}>20</MenuItem>
        </Select>
      </Box>

      <Pagination
        count={totalPages}
        page={page}
        onChange={(e, value) => onPageChange(value)}
        color="primary"
        siblingCount={isMobile ? 0 : 1}
        boundaryCount={isMobile ? 1 : 1}
        sx={{
          "& .MuiPaginationItem-root": {
            borderRadius: "8px",
            fontSize: "14px",
            minWidth: "28px",
            height: "28px",
            color: "#000",
            backgroundColor: "#fff",
            "&:hover": {
              backgroundColor: "#fff",
            },
          },
          "& .MuiPaginationItem-root.Mui-selected": {
            backgroundColor: "#fff",
            color: "#007AFF",
            "&:hover": {
              backgroundColor: "#fff",
              color: "#007AFF",
            },
          },
        }}
      />
    </Box>
  );
};

export default TablePagination;
